from commonutils.utils import CustomEnum

class DatabaseTables(CustomEnum):
    EVENT = 'event'
    APPS = 'apps'
    PUSH_NOTIFICATION = 'push_notification'
    NOTIFICATION_REQUEST_LOG = 'notification_request_log'
    EMAIL_CONTENT = 'email_content'
    SMS_CONTENT = 'sms_content'
    GENERIC_DATA_STORE = 'generic_data_store'
    WHATSAPP_CONTENT = 'whatsapp_content'
    NOTIFICATION_REQUEST_ATTEMPT = 'notification_request_attempt'
