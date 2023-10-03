from enum import Enum


class EventName(Enum):
    DND_ON_MSG_EVENT = "dnd_on_msg_event"
    DND_OFF_MSG_EVENT = "dnd_off_msg_event"
    DEFAULT_REPLY_MSG_EVENT = "default_reply_msg_event"
    POST_DND_ON_MSG_EVENT = "post_dnd_on_msg_event"
    INVALID_MEDIA_RX_MSG_EVENT = "invalid_media_rx_msg_event"
    SUCCESS_MSG_POST_UPLOAD_RX_EVENT = "success_msg_post_upload_rx_event"
    NO_ORDER_MSG_POST_UPLOAD_RX_EVENT = "no_order_msg_post_upload_rx_event"
    INVALID_MSG_TYPE_EVENT = "invalid_msg_type_event"

    @classmethod
    def get_all_event_name(cls):
        return [variable.value for variable in cls]


class Sms:
    CONTENT = "content"
    CONTENT_COLUMNS = ["id", "content", "event_id"]
