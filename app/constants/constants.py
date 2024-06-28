from enum import Enum


MAX_DEVICES_FOR_PUSH = 10


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
    ADD_ACTION_REQUIRED_PARAMS = ["app_name", "event_name", "user_email"]
    EVENT_PRIORITY = "priority"
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


class EventType(Enum):
    PROMOTIONAL = "promotional"
    TRANSACTIONAL = "transactional"
    OTHER = "other"


class SyncDispatcher:
    ENDPOINT = "/notify"
    METHOD = "POST"
