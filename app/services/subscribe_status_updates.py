import asyncio

from torpedo import CONFIG

from ..utilities.pubsub import SQSWrapper

from .status_updates import NotificationStatusUpdate

subs_status_update_config = CONFIG.config['SUBSCRIBE_NOTIFICATION_STATUS_UPDATES']


class SubscribeStatusUpdate:

    _subscriber_instances = list()

    for i in range (subs_status_update_config['SUBSCRIBE_TO']['SUBSCRIBERS_COUNT']):
        _subscriber_instances.append(
            SQSWrapper(
                subs_status_update_config['SUBSCRIBE_TO']['QUEUE_NAME'],
                config=subs_status_update_config,
                handler=NotificationStatusUpdate.handle_status_update, instance_identifier='NSU-{}'.format(i+1),
                subscribe_delay_seconds=subs_status_update_config.get('SUBSCRIBE_DELAY_SECONDS', 5)
            )
        )

    @classmethod
    async def setup_subscription(cls):
        for subs_instance in cls._subscriber_instances:
            asyncio.create_task(subs_instance.subscribe_forever(max_no_of_messages=5))
