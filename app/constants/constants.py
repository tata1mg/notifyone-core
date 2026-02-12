from enum import Enum
from commonutils.utils import CustomEnum


URL_SHORTENER_START_PATTERN = "__URL_SHORTNER_START__"
URL_SHORTENER_END_PATTERN = "__URL_SHORTNER_END__"
MAX_DEVICES_FOR_PUSH = 10
TRUNCATE_MAX_LEN = 5000


class Action(Enum):
    ON = 1
    OFF = 0


class TriggerLimit(Enum):
    INFINITE = -1
    SINGLE = 1


class Event:
    CREATE_EVENT_REQUIRED_PARAMS = [
        "app_name",
        "event_name",
        "user_email",
        "priority",
        "event_type",
    ]
    TRIGGER_LIMIT = 'trigger_limit'
    ADD_ACTION_REQUIRED_PARAMS = ["app_name", "event_name", "user_email"]
    EVENT_UPDATE_REQUIRED_PARAMS = ['app_name', 'event_name', 'event_type', 'priority', 'callback_enabled', 'payload']
    EVENT_PRIORITY = "priority"
    DYNAMIC_CHANNELS = "dynamic_channels"
    EVENT_TYPE = "event_type"
    NEW_EVENT_CREATED_MESSAGE = "New event created with event_name = {event_name},app_name = {app_name} by {user_email}."
    NEW_ACTION_ADDED_MESSAGE = "New action added in event_name = {event_name},app_name = {app_name} by {user_email}."
    KEY_DELIMITER = "_"
    COLUMNS = ["event_name", "actions", "app_name", "triggers_limit"]
    EVENT_NAME = "event_name"
    APP_NAME = "app_name"
    USER_EMAIL = "user_email"
    REMOVE_ID = "id"
    EVENT_ID = "event_id"
    SOFT_DELETE_DEFAULT_VALUE = False
    DEFAULT_LIMIT = 1000
    DEFAULT_OFFSET = 0
    ID = "id"

class SyncDispatcher:
    ENDPOINT = "/notify"
    METHOD = "POST"


class Redis:
    REDIS_NAMESPACE = 'notification_core_redis'
    REDIS_EXPIRY_TIME_MED = 60 * 60
    KEY_DELIMITER = '_'


class RedisKeyPrefixes:
    EVENT_BODY_LATEST_VERSION = 'event_body_latest_version'
