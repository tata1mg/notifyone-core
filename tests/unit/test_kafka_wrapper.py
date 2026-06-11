"""
Unit tests for core KafkaWrapper.
Stubs out commonutils/torpedo so this runs without the full pipenv install.
"""
import asyncio
import dataclasses
import enum
import importlib.util
import json
import sys
import types
import zlib
import base64
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Bootstrap stubs
# ---------------------------------------------------------------------------

def _ensure_stub(name, **attrs):
    if name not in sys.modules:
        mod = types.ModuleType(name)
        for k, v in attrs.items():
            setattr(mod, k, v)
        sys.modules[name] = mod
    return sys.modules[name]


_ensure_stub("commonutils", BaseSQSWrapper=object)
_ensure_stub("commonutils.utils", CustomEnum=str)


class _FakeCONFIG:
    config = {"NOTIFICATION_REQUEST": {"QUEUE_BACKEND": "kafka", "KAFKA": {}, "SUBSCRIBE_TO": {}}}


_ensure_stub("torpedo", CONFIG=_FakeCONFIG())
_ensure_stub("torpedo.exceptions")


class _NotificationRequestLogStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


_ensure_stub("app.constants", NotificationRequestLogStatus=_NotificationRequestLogStatus)


@dataclasses.dataclass
class _PublishResult:
    is_success: bool
    status: object
    message: object = None
    unhandled_exception: bool = False
    operator_details: object = None


class _Publisher:
    async def publish(self, data):
        raise NotImplementedError


_ensure_stub("app.service_clients")
_ensure_stub(
    "app.service_clients.publisher",
    PublishResult=_PublishResult,
    Publisher=_Publisher,
)
_ensure_stub("app.utilities")
_ensure_stub("app.utilities.utils", json_dumps=json.dumps)
_ensure_stub("app.utilities.pubsub")

_CORE_ROOT = "/opt/1mg/open_source/notifyone/notifyone-core"
if _CORE_ROOT not in sys.path:
    sys.path.insert(0, _CORE_ROOT)

_spec = importlib.util.spec_from_file_location(
    "core_kafka_wrapper",
    f"{_CORE_ROOT}/app/utilities/pubsub/kafka/kafka_wrapper.py",
)
_kafka_wrapper_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_kafka_wrapper_mod)

KafkaWrapper = _kafka_wrapper_mod.KafkaWrapper


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def kafka_config():
    return {
        "QUEUE_BACKEND": "kafka",
        "KAFKA": {
            "BOOTSTRAP_SERVERS": "localhost:9092",
            "MAX_RETRY_ATTEMPTS": 3,
        },
    }


def _make_mock_msg(body_bytes, headers=None, partition=0, offset=0, topic="test-topic"):
    msg = MagicMock()
    msg.value = body_bytes
    msg.headers = headers or []
    msg.partition = partition
    msg.offset = offset
    msg.topic = topic
    return msg


class _AsyncIter:
    def __init__(self, items):
        self._it = iter(items)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self._it)
        except StopIteration:
            raise StopAsyncIteration


def _make_mock_consumer(msgs):
    mock_consumer = MagicMock()
    mock_consumer.start = AsyncMock()
    mock_consumer.stop = AsyncMock()
    mock_consumer.commit = AsyncMock()
    mock_consumer.seek = MagicMock()  # synchronous per aiokafka==0.10.0 API
    mock_consumer.__aiter__ = lambda self: _AsyncIter(msgs)
    return mock_consumer


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_publish_success(kafka_config):
    """publish() returns PublishResult(is_success=True) on success."""
    with patch.object(_kafka_wrapper_mod, "AIOKafkaProducer") as MockProducer:
        mock_producer = AsyncMock()
        MockProducer.return_value = mock_producer
        mock_producer.send_and_wait = AsyncMock(return_value=None)

        wrapper = KafkaWrapper(queue_name="test-topic", config=kafka_config)
        result = await wrapper.publish({"key": "value"})

    assert result.is_success is True
    mock_producer.send_and_wait.assert_called_once()


@pytest.mark.asyncio
async def test_publish_failure(kafka_config):
    """publish() returns is_success=False when producer raises an exception."""
    with patch.object(_kafka_wrapper_mod, "AIOKafkaProducer") as MockProducer:
        mock_producer = AsyncMock()
        MockProducer.return_value = mock_producer
        mock_producer.send_and_wait = AsyncMock(side_effect=Exception("kafka error"))

        wrapper = KafkaWrapper(queue_name="test-topic", config=kafka_config)
        result = await wrapper.publish({"key": "value"})

    assert result.is_success is False
    assert "kafka error" in result.message


@pytest.mark.asyncio
async def test_subscribe_forever_calls_event_handler_with_decoded_body(kafka_config):
    """subscribe_forever calls event_handler with decoded body string."""
    body = json.dumps({"hello": "world"})
    msg = _make_mock_msg(body.encode("utf-8"))

    handler = AsyncMock(return_value=True)

    with patch.object(_kafka_wrapper_mod, "AIOKafkaProducer"), \
         patch.object(_kafka_wrapper_mod, "AIOKafkaConsumer") as MockConsumer:
        MockConsumer.return_value = _make_mock_consumer([msg])

        wrapper = KafkaWrapper(
            queue_name="test-topic",
            config=kafka_config,
            handler=handler,
            instance_identifier="test-1",
        )
        await wrapper.subscribe_forever()

    handler.assert_called_once()
    received_body = handler.call_args[0][0]
    received_identifier = handler.call_args[0][1]
    assert received_body == body
    assert received_identifier == "test-1"


@pytest.mark.asyncio
async def test_subscribe_forever_successful_handler_causes_commit(kafka_config):
    """Successful handler invocation causes consumer.commit() to be called."""
    body = json.dumps({"x": 1})
    msg = _make_mock_msg(body.encode("utf-8"))
    mock_consumer = _make_mock_consumer([msg])
    handler = AsyncMock(return_value=True)

    with patch.object(_kafka_wrapper_mod, "AIOKafkaProducer"), \
         patch.object(_kafka_wrapper_mod, "AIOKafkaConsumer") as MockConsumer:
        MockConsumer.return_value = mock_consumer

        wrapper = KafkaWrapper(
            queue_name="test-topic", config=kafka_config, handler=handler
        )
        await wrapper.subscribe_forever()

    mock_consumer.commit.assert_called_once()


@pytest.mark.asyncio
async def test_failing_handler_does_not_commit_below_threshold(kafka_config):
    """A handler returning False on the first attempt does NOT commit (below max retries)
    and consumer.seek() is called so the message is re-fetched in the current session."""
    cfg = {
        "QUEUE_BACKEND": "kafka",
        "KAFKA": {"BOOTSTRAP_SERVERS": "localhost:9092", "MAX_RETRY_ATTEMPTS": 3},
    }
    body = json.dumps({"x": 1})
    # Only one message delivered, handler fails once (count 1 < threshold 3)
    msg = _make_mock_msg(body.encode("utf-8"), partition=0, offset=42, topic="test-topic")
    mock_consumer = _make_mock_consumer([msg])
    handler = AsyncMock(return_value=False)

    with patch.object(_kafka_wrapper_mod, "AIOKafkaProducer"), \
         patch.object(_kafka_wrapper_mod, "AIOKafkaConsumer") as MockConsumer, \
         patch.object(_kafka_wrapper_mod, "TopicPartition") as MockTP:
        MockConsumer.return_value = mock_consumer

        wrapper = KafkaWrapper(
            queue_name="test-topic", config=cfg, handler=handler
        )
        await wrapper.subscribe_forever()

    mock_consumer.commit.assert_not_called()
    # seek() must be called to reschedule re-delivery within the same session
    mock_consumer.seek.assert_called_once()
    MockTP.assert_called_once_with("test-topic", 0)  # topic, partition


@pytest.mark.asyncio
async def test_dead_letter_after_max_retries(kafka_config):
    """After MAX_RETRY_ATTEMPTS handler failures, message is committed (skipped) as dead.
    The handler must be called exactly MAX_RETRY_ATTEMPTS (3) times before dead-lettering."""
    cfg = {
        "QUEUE_BACKEND": "kafka",
        "KAFKA": {"BOOTSTRAP_SERVERS": "localhost:9092", "MAX_RETRY_ATTEMPTS": 3},
    }
    body = json.dumps({"x": 1})
    # Same partition/offset = same message key; inject 3 copies to simulate the seek()
    # re-delivery that occurs after each failure below the threshold.
    msgs = [
        _make_mock_msg(body.encode("utf-8"), partition=0, offset=42, topic="test-topic"),
        _make_mock_msg(body.encode("utf-8"), partition=0, offset=42, topic="test-topic"),
        _make_mock_msg(body.encode("utf-8"), partition=0, offset=42, topic="test-topic"),
    ]
    mock_consumer = _make_mock_consumer(msgs)
    handler = AsyncMock(return_value=False)

    with patch.object(_kafka_wrapper_mod, "AIOKafkaProducer"), \
         patch.object(_kafka_wrapper_mod, "AIOKafkaConsumer") as MockConsumer:
        MockConsumer.return_value = mock_consumer

        wrapper = KafkaWrapper(
            queue_name="test-topic", config=cfg, handler=handler
        )
        await wrapper.subscribe_forever()

    # Handler must be called exactly MAX_RETRY_ATTEMPTS times before dead-lettering
    assert handler.call_count == 3
    # Exactly 1 commit after 3 failures (dead-letter skip)
    mock_consumer.commit.assert_called_once()


@pytest.mark.asyncio
async def test_subscribe_forever_decompresses_compressed_message(kafka_config):
    """Compressed message header causes decompression before handler call."""
    original_body = json.dumps({"compressed": True})
    compressed = zlib.compress(original_body.encode("utf-8"), 1)
    encoded = base64.b64encode(compressed).decode("utf-8")
    msg = _make_mock_msg(
        encoded.encode("utf-8"),
        headers=[("compressedMessage", b"yes")],
    )
    mock_consumer = _make_mock_consumer([msg])
    handler = AsyncMock(return_value=True)

    with patch.object(_kafka_wrapper_mod, "AIOKafkaProducer"), \
         patch.object(_kafka_wrapper_mod, "AIOKafkaConsumer") as MockConsumer:
        MockConsumer.return_value = mock_consumer

        wrapper = KafkaWrapper(
            queue_name="test-topic", config=kafka_config, handler=handler
        )
        await wrapper.subscribe_forever()

    received_body = handler.call_args[0][0]
    assert received_body == original_body
