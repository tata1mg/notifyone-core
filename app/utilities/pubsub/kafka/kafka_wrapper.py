import asyncio
import json
import logging
import zlib
import base64

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer

from app.constants import NotificationRequestLogStatus
from app.service_clients.publisher import Publisher, PublishResult
from app.utilities.utils import json_dumps

logger = logging.getLogger(__name__)


class KafkaWrapper(Publisher):

    def __init__(
            self,
            queue_name: str,
            config: dict = {},
            handler: object = None,
            is_compression_enabled: bool = False,
            instance_identifier: str = None,
            subscribe_delay_seconds: int = None,
    ):
        config = config or {}
        self.queue_name = queue_name
        self._kafka_config = config.get("KAFKA") or {}
        self.bootstrap_servers = self._kafka_config.get("BOOTSTRAP_SERVERS", "localhost:9092")
        self.max_retry_attempts = self._kafka_config.get("MAX_RETRY_ATTEMPTS", 3)
        self.is_compression_enabled = is_compression_enabled
        self.event_handler = handler
        self.instance_identifier = instance_identifier
        self.subscribe_delay_seconds = subscribe_delay_seconds
        self._producer = None
        self._consumer = None
        self._init_lock = asyncio.Lock()
        self._is_client_created = False
        self._retry_counts = {}

    async def init(self) -> None:
        if not self._is_client_created:
            async with self._init_lock:
                if not self._is_client_created:
                    self._producer = AIOKafkaProducer(
                        bootstrap_servers=self.bootstrap_servers
                    )
                    await self._producer.start()
                    self._is_client_created = True

    async def close_client(self) -> None:
        if self._producer is not None:
            await self._producer.stop()
            self._producer = None
            self._is_client_created = False
        if self._consumer is not None:
            await self._consumer.stop()
            self._consumer = None

    async def publish(self, payload: dict, attributes: dict = None, **kwargs) -> PublishResult:
        await self.init()
        payload_json = json_dumps(payload)
        headers = []
        if self.is_compression_enabled:
            payload_json = self._compress_message(payload_json)
            headers.append(("compressedMessage", b"yes"))
        try:
            await self._producer.send_and_wait(
                self.queue_name,
                value=payload_json.encode("utf-8"),
                headers=headers,
            )
            return PublishResult(
                is_success=True,
                status=NotificationRequestLogStatus.SUCCESS,
                message="Message successfully published to Kafka",
            )
        except Exception as err:
            logger.error("Failed to publish to Kafka topic %s: %s", self.queue_name, str(err))
            return PublishResult(
                is_success=False,
                status=NotificationRequestLogStatus.FAILED,
                message=str(err),
            )

    async def subscribe_forever(self, **kwargs) -> None:
        if self.subscribe_delay_seconds and self.subscribe_delay_seconds > 0:
            await asyncio.sleep(self.subscribe_delay_seconds)

        group_id = "ns-core-{}".format(self.queue_name)
        consumer = AIOKafkaConsumer(
            self.queue_name,
            bootstrap_servers=self.bootstrap_servers,
            group_id=group_id,
            auto_offset_reset="earliest",
            enable_auto_commit=False,
        )
        self._consumer = consumer
        await consumer.start()
        try:
            async for msg in consumer:
                msg_key = (msg.partition, msg.offset)
                try:
                    body = msg.value.decode("utf-8")
                    # Check for compression header
                    headers_dict = {k: v for k, v in (msg.headers or [])}
                    if headers_dict.get("compressedMessage") == b"yes":
                        body = self._decompress_message(body)
                    retry_count = self._retry_counts.get(msg_key, 0) + 1
                    self._retry_counts[msg_key] = retry_count
                    is_success = await self.event_handler(
                        body,
                        self.instance_identifier,
                        message_receive_count=retry_count,
                    )
                    if is_success:
                        await consumer.commit()
                        self._retry_counts.pop(msg_key, None)
                    else:
                        if retry_count >= self.max_retry_attempts:
                            logger.error(
                                "Dead-lettering message on topic %s partition %d offset %d after %d attempts",
                                msg.topic,
                                msg.partition,
                                msg.offset,
                                retry_count,
                            )
                            await consumer.commit()
                            self._retry_counts.pop(msg_key, None)
                        # else: loop continues, message will be re-delivered
                except Exception as e:
                    retry_count = self._retry_counts.get(msg_key, 0) + 1
                    self._retry_counts[msg_key] = retry_count
                    if retry_count >= self.max_retry_attempts:
                        logger.error(
                            "Dead-lettering message on topic %s partition %d offset %d after exception: %s",
                            msg.topic if hasattr(msg, "topic") else self.queue_name,
                            msg.partition if hasattr(msg, "partition") else -1,
                            msg.offset if hasattr(msg, "offset") else -1,
                            str(e),
                        )
                        await consumer.commit()
                        self._retry_counts.pop(msg_key, None)
                    logger.exception(
                        "Error processing message from Kafka topic %s: %s",
                        self.queue_name,
                        str(e),
                    )
        finally:
            await consumer.stop()

    async def get_messages_count(self) -> int:
        group_id = "ns-core-{}".format(self.queue_name)
        consumer = AIOKafkaConsumer(
            self.queue_name,
            bootstrap_servers=self.bootstrap_servers,
            group_id=group_id,
            auto_offset_reset="earliest",
            enable_auto_commit=False,
        )
        await consumer.start()
        try:
            partitions = consumer.assignment()
            end_offsets = await consumer.end_offsets(list(partitions))
            total_lag = 0
            for tp, end_offset in end_offsets.items():
                committed = await consumer.committed(tp)
                committed_offset = committed if committed is not None else 0
                total_lag += max(0, end_offset - committed_offset)
            return total_lag
        finally:
            await consumer.stop()

    @staticmethod
    def _compress_message(message: str) -> str:
        compressed = zlib.compress(message.encode("utf-8"), 1)
        return base64.b64encode(compressed).decode("utf-8")

    @staticmethod
    def _decompress_message(compressed_msg: str) -> str:
        decoded = base64.b64decode(compressed_msg.encode("utf-8"))
        return zlib.decompress(decoded).decode("utf-8")
