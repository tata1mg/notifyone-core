from torpedo import CONFIG
from torpedo.constants import ListenerEventTypes
from redis_wrapper import cache_registry
from asyncio import BaseEventLoop
from app.repositories.content_log import ContentLogRepository
from app.services import SubscribeNotificationRequest, SubscribeStatusUpdate
from app.services.email import EmailHandler
from app.services.sms import SMSHandler
from app.services.push import PushHandler
from app.services.whatsapp import WhatsappHandler
from app.utilities.drivers import CustomJinjaEnvironment

from .options_routes import setup_options


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

async def initialize_redis_caches(app):
    cache_config = CONFIG.config["REDIS_CACHE_HOSTS"]
    cache_registry.from_config(cache_config)


def exc_handler(self: BaseEventLoop, context: dict) -> None:
    """
    Custom exception handler to filter out specific messages.
    :param self: The event loop instance
    :param context: The context dictionary containing exception details
    :return: None
    """
    message = context.get("message")
    if message not in ["Unclosed connector", "Unclosed client session"]:
        BaseEventLoop.default_exception_handler(self, context)


async def setup_custom_exc_handler(app, loop):
    """
    Set up the custom exception handler for the event loop.
    :param app: The current app instance
    :param loop: The running event loop
    :return: None
    """
    loop.set_exception_handler(exc_handler)


listeners = [
    (initialize_redis_caches, ListenerEventTypes.BEFORE_SERVER_START.value),
    (subscribe_for_notification_requests, ListenerEventTypes.AFTER_SERVER_START.value),
    (subscribe_for_status_updates, ListenerEventTypes.AFTER_SERVER_START.value),
    (setup_notification_channel_handlers, ListenerEventTypes.AFTER_SERVER_START.value),
    (initialize_jinja_environment, ListenerEventTypes.AFTER_SERVER_START.value),
    (setup_repositories, ListenerEventTypes.AFTER_SERVER_START.value),
    (setup_custom_exc_handler, ListenerEventTypes.BEFORE_SERVER_START.value),
]
