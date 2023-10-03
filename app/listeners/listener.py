from torpedo import CONFIG
from torpedo.constants import ListenerEventTypes

from app.repositories.content_log import ContentLogRepository
from app.services import SubscribeNotificationRequest, SubscribeStatusUpdate
from app.services.email import EmailHandler
from app.services.sms import SMSHandler
from app.services.push import PushHandler
from app.services.whatsapp import WhatsappHandler
from app.utilities.drivers import CustomJinjaEnvironment


async def subscribe_for_notification_requests(app, loop):
    await SubscribeNotificationRequest.setup_subscription()


async def subscribe_for_status_updates(app, loop):
    await SubscribeStatusUpdate.setup_subscription()


async def setup_notification_channel_handlers(app, loop):
    EmailHandler.setup()
    SMSHandler.setup()
    WhatsappHandler.setup()
    PushHandler.setup()


async def initialize_jinja_environment(app, loop):
    await CustomJinjaEnvironment.set_jinja_env()


async def setup_repositories(app, loop):
    ContentLogRepository.init(
        config=CONFIG.config.get("CONTENT_LOG", {}).get("S3")
    )


listeners = [
    (subscribe_for_notification_requests, ListenerEventTypes.AFTER_SERVER_START.value),
    (subscribe_for_status_updates, ListenerEventTypes.AFTER_SERVER_START.value),
    (setup_notification_channel_handlers, ListenerEventTypes.AFTER_SERVER_START.value),
    (initialize_jinja_environment, ListenerEventTypes.AFTER_SERVER_START.value),
    (setup_repositories, ListenerEventTypes.AFTER_SERVER_START.value),
]
