import asyncio

from torpedo import CONFIG

from ..utilities.pubsub import SQSWrapper

from .notification_request import NotificationRequest

notification_request_config = CONFIG.config['NOTIFICATION_REQUEST']


class SubscribeNotificationRequest:

    _subscriber_instances = list()

    for priority, details in notification_request_config['SUBSCRIBE_TO'].items():
        for i in range(details['SUBSCRIBERS_COUNT']):
            _subscriber_instances.append(
                SQSWrapper(
                    details['QUEUE_NAME'], config=notification_request_config,
                    handler=NotificationRequest.handle_notification_request_async,
                    instance_identifier='{}-{}'.format(priority, i+1),
                    subscribe_delay_seconds=notification_request_config.get('SUBSCRIBE_DELAY_SECONDS', 5)
                )
            )

    @classmethod
    async def setup_subscription(cls):
        for subs_instance in cls._subscriber_instances:
            asyncio.create_task(subs_instance.subscribe_forever(max_no_of_messages=5))
