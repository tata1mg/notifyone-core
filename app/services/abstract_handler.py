from typing import Any, Dict

from app.constants import SyncDispatcher, EventPriority
from app.models.notification_core import EventModel
from app.utilities.pubsub import SQSWrapper
from app.utilities.http import RestApiClientWrapper


class _PriorityBasedDispatcher:
    def __init__(self, config: Dict[str, Any]) -> None:
        dispatcher_config = config.get("config")
        sync_dispatcher_config = config.get("sync_dispatcher_config")
        async_dispatcher_config = config.get("async_dispatcher_config")

        self.sync_dispatcher = None
        self.async_dispatcher = None

        self._create_dispatchers(
            dispatcher_config=dispatcher_config,
            sync_config=sync_dispatcher_config,
            async_config=async_dispatcher_config,
        )

    def _create_dispatchers(
        self,
        dispatcher_config: Dict[str, Any],
        sync_config: Dict[str, Any],
        async_config: Dict[str, Any],
    ):
        if not self.async_dispatcher:
            queue_name = async_config.pop("QUEUE_NAME")
            self.async_dispatcher = SQSWrapper(queue_name, config=dispatcher_config)
        if not self.sync_dispatcher:
            host = sync_config.pop("HOST")
            self.sync_dispatcher = RestApiClientWrapper(
                host=host,
                endpoint=SyncDispatcher.ENDPOINT,
                method=SyncDispatcher.METHOD,
            )

    async def publish(self, payload: Dict[str, Any], priority: EventPriority):
        if priority != EventPriority.CRITICAL:
            return await self.async_dispatcher.publish(payload)
        return await self.sync_dispatcher.publish(payload)


class AbstractHandler:

    """
    An abstract handler to handle a notification request.
    Handlers for each channel must extend this class
    """

    _channel_config = None
    _dispatch_notification_config = None
    _dispatch_notification = None

    @classmethod
    def setup(cls):
        sync_channel_config = cls._channel_config.get("SYNC_CHANNEL")
        async_channel_config = cls._channel_config.get("ASYNC_CHANNEL")

        cls._dispatch_notification = _PriorityBasedDispatcher(
            {
                "config": cls._dispatch_notification_config,
                "sync_dispatcher_config": sync_channel_config,
                "async_dispatcher_config": async_channel_config,
            }
        )

    @classmethod
    async def handle(
        cls, event: EventModel, request_body, notification_request_log_row
    ):
        """
        Subclass for a channel must implement this to handle the notification requests
        """
        pass
