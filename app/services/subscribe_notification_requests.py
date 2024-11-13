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

    @classmethod
    async def get_messages_in_priority_queues(cls):
        messages = dict()
        for priority in notification_request_config['SUBSCRIBE_TO'].keys():
            instance_identifier = "{}-{}".format(priority, 1)
            messages_count = None
            for subs in cls._subscriber_instances:
                if subs.instance_identifier == instance_identifier:
                    messages_count = int(await subs.get_messages_count())
                    break
            messages[priority] = messages_count
        return messages
