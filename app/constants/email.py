class Email:
    INCLUDE_START = '$include_start-'
    INCLUDE_END = '-$include_end'
    SUBJECT = 'subject'
    DESCRIPTION = 'description'
    CONTENT = 'content'
    NAME = 'name'
    CONTENT_COLUMNS=['id', 'event_id', 'name', 'description', 'subject', 'content','updated_by']
    REDIS_EXPIRY_TIME_LONG = 24 * 60 * 60
    