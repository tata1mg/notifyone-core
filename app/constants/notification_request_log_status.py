from commonutils.utils import CustomEnum


class NotificationRequestLogStatus(str, CustomEnum):
    NEW = 'NEW'
    INITIATED = 'INITIATED'
    FAILED = 'FAILED'
    SUCCESS = 'SUCCESS'
    USER_OPT_OUT = 'USER_OPT_OUT'
    NOT_ELIGIBLE = 'NOT_ELIGIBLE'

    def __str__(self):
        return self.value

    @classmethod
    def allowed_statuses_for_status_update(cls):
        return [cls.SUCCESS.value, cls.FAILED.value]

    @classmethod
    def allowed_statues_for_processed_status_update(cls):
        return [cls.NEW.value]

    @classmethod
    def trigger_successful_statuses(cls):
        return [cls.SUCCESS.value, cls.INITIATED.value, cls.NOT_ELIGIBLE.value, cls.USER_OPT_OUT.value]
