import asyncio
import logging
import zlib
import base64

from commonutils import BaseSQSWrapper

from app.constants import NotificationRequestLogStatus
from app.models.sqs_message import SQSMessage
from app.service_clients.publisher import Publisher, PublishResult
from app.utilities.utils import json_dumps

logger = logging.getLogger()


class SQSWrapper(Publisher):

    def __init__(
            self,
            queue_name: str,
            config: dict = {},
            handler: object = None,
            is_compression_enabled: bool = False,
            instance_identifier: str = None,
            subscribe_delay_seconds=None
    ):
        config = config or {"SQS": {}}
        self.queue_name = queue_name
        self.sqs_manager = BaseSQSWrapper(config)
        self._create_client_lock = asyncio.Lock()
        self.event_handler = handler
        self.is_client_created = False
        self.is_compression_enabled = is_compression_enabled
        self.instance_identifier = instance_identifier
        self.subscribe_delay_seconds = subscribe_delay_seconds

    def __del__(self):
        asyncio.create_task(self.close_client())

    async def close_client(self):
        await self.sqs_manager.close()

    async def init(self):
        if not self.is_client_created:
            async with self._create_client_lock:
                if not self.is_client_created:
                    await self.sqs_manager.get_sqs_client(queue_name=self.queue_name)
            self.is_client_created = True

    async def publish(self, payload: dict, attributes=None, **kwargs):
        await self.init()
        if self.is_compression_enabled:
            payload = self.compress_payload(payload)
        else:
            payload = json_dumps(payload)

        try:
            response = await self.sqs_manager.publish_to_sqs(
                payload=payload, attributes=attributes, batch=False, **kwargs
            )
            if response:
                publish_result = PublishResult(
                    is_success=True, status=NotificationRequestLogStatus.SUCCESS,
                    message="Message successfully published to SQS"
                )
            else:
                publish_result = PublishResult(
                    is_success=False, status=NotificationRequestLogStatus.FAILED,
                    message="Could not publish to SQS"
                )
        except Exception as err:
            publish_result = PublishResult(
                is_success=False, status=NotificationRequestLogStatus.FAILED,
                message=str(err)
            )
        return publish_result

    async def purge(self, receipt_handle):
        """
        purge sqs message
        """
        response = await self.sqs_manager.purge(receipt_handle)
        return response

    async def subscribe(self, **kwargs) -> [SQSMessage]:
        """
        Subscribe from queue
        """
        await self.init()
        subscribed_messages = list()
        max_no_of_messages = kwargs.get("max_no_of_messages") or 1
        messages = await asyncio.shield(self.sqs_manager.subscribe(max_no_of_messages=max_no_of_messages))
        if messages and 'Messages' in messages:
            messages = messages['Messages']
            for msg in messages:
                sqs_message = SQSMessage(msg)
                if sqs_message.message_attributes.compressed_message:
                    sqs_message.body = self.decompress_message(sqs_message.body)
                subscribed_messages.append(sqs_message)
        return subscribed_messages

    async def subscribe_forever(self, **kwargs):
        """
        Continuously subscribe to the queue
        """
        # We get "Unable to locate credentials" error immediately after the service start for a few seconds.
        # To make sure this does not happen, we will put the subscribe process on sleep for x seconds before it starts
        # subscribing from the designated queue.
        if self.subscribe_delay_seconds and self.subscribe_delay_seconds > 0:
            await asyncio.shield(asyncio.sleep(self.subscribe_delay_seconds))

        while True:
            try:

                messages = await asyncio.shield(self.subscribe(**kwargs))
                for message in messages:
                    is_success = await self.event_handler(
                        message.body, self.instance_identifier,
                        message_receive_count=message.attributes.approximate_receive_count
                    )
                    if is_success:
                        receipt_handle = message.receipt_handle
                        await self.purge(receipt_handle=receipt_handle)
            except Exception as e:
                logger.exception('Error in subscribing from SQS queue {} - {}'.format(self.queue_name, str(e)))
                await asyncio.sleep(1)

    async def get_messages_count(self) -> int:
        await self.init()
        queue_url = await self.sqs_manager.get_queue_url(self.queue_name)
        resp = await self.sqs_manager.get_queue_attributes(
            queue_url, attribute_names=["ApproximateNumberOfMessages"]
        )
        return resp["Attributes"]["ApproximateNumberOfMessages"]

    @staticmethod
    def compress_payload(payload):
        compressed_payload = zlib.compress(json_dumps(payload).encode("utf-8"), 1)
        encoded_payload = base64.b64encode(compressed_payload).decode("utf-8")
        return encoded_payload

    @staticmethod
    def decompress_message(compressed_msg) -> dict:
        decoded_str = base64.b64decode(compressed_msg.encode('utf-8'))
        decompressed_msg = zlib.decompress(decoded_str).decode('utf-8')
        return decompressed_msg
