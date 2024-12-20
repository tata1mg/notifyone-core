from pydantic.main import validate_model
from torpedo.exceptions import BadRequestException

from app.constants import NotificationChannels, NotificationRequestLogStatus
from app.repositories.notification_request_log import NotificationRequestLogRepository
from app.utilities import epoch_to_str_date
from app.utilities.validators.base import validate_mobile, validate_email


class DashboardActivityFeedScreen:

    @classmethod
    async def search_sent_notifications(cls, data: dict):
        channel = data.get("channel") or None
        request_id = data.get("request_id") or None
        mobile = data.get("mobile") or None
        email = data.get("email") or None
        limit = data.get("limit") or 10
        offset = data.get("offset") or 0
        try:
            limit = int(limit)
        except ValueError:
            raise BadRequestException("Invalid value for limit")
        try:
            offset = int(offset)
        except ValueError:
            raise BadRequestException("Invalid value for offset")

        if channel and not NotificationChannels.get_enum(channel):
            raise BadRequestException("Invalid channel")
        if mobile and not validate_mobile(mobile):
            raise BadRequestException("Invalid mobile number format")
        if email and not validate_email(email):
            raise BadRequestException("Invalid email format")

        select_filters = dict()

        if channel:
            select_filters["channel"] = channel
        if request_id:
            select_filters["notification_request_id"] = request_id
        if email:
            select_filters["sent_to"] = email
        if mobile:
            select_filters["sent_to"] = mobile

        if not select_filters:
            raise BadRequestException("Please provide filters to search")

        triggered_notifications = await NotificationRequestLogRepository.get_notification_request_log(
            **select_filters, limit=limit, offset=offset, order_by="id"
        )
        tn_count = await NotificationRequestLogRepository.get_notification_request_log_count(**select_filters)
        resp_data = list()
        for tn in triggered_notifications:
            tn.metadata = None
            if tn.status == NotificationRequestLogStatus.SUCCESS.value:
                tn.message = None
            tn_dict = await tn.to_dict()
            tn_dict['created'] = epoch_to_str_date(int(tn_dict['created'].timestamp()))
            tn_dict['updated'] = epoch_to_str_date(int(tn_dict['updated'].timestamp()))
            resp_data.append(tn_dict)

        return {
            "limit": limit,
            "offset": offset,
            "total": tn_count,
            "notifications": resp_data
        }
