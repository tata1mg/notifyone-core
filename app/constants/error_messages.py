from commonutils.utils import CustomEnum

class ErrorMessages(CustomEnum):
    MISSING_REQUIRED_PARAM = 'missing required param'
    INVALID_EVENT_ATTRIBUTE = 'invalid event attribute requested'
    PUSH_EVENT_NOT_FOUND_IN_DB = 'Push notification does not exist for this notification event'
    APP_NOT_CONFIGURED = 'App details are not present in DB. Please configure the app before sending the email'
    NO_REGISTERED_DEVICE_FOUND = "No registered devices found in device service"
    NO_SEND_ADDRESS_FOUND = 'No address found to send the notification'
    SEND_ADDRESS_NOT_ALLOWED_ON_TEST_ENV = 'The send address is not allowed on this testing environment'
    EVENT_ALREADY_CREATED_ERROR = '{} event with app_name {} already exist,' \
                                  ' add more action to it, or create new event'
    ACTION_ALREADY_ADDED_ERROR = '{} action is already added in given event'
    EMAIL_DATA_NOT_FOUND_ERROR = 'No email_data found to create email content entry'
    PUSH_DATA_NOT_FOUND_ERROR = 'No push_data found to create push_notification entry'
    WHATSAPP_DATA_NOT_FOUND_ERROR = 'No what_data found to create whatsapp_content_entry'
    EMPTY_ACTION_ERROR = 'No actions are found in the event, empty action is not allowed'
    INVALID_USER_EMAIL = 'Invalid user_email'
    NOT_ALLOWED_ACTION_ERROR = 'Currently, {} event creation is not allowed'
    REQUIRED_FIELD = 'In {} field {} is required'
    SMS_DATA_NOT_FOUND_ERROR = 'No sms data found to create sms content entry'
