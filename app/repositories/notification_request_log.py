from tortoise_wrapper.wrappers import ORMWrapper

from app.constants import DatabaseTables
from app.models.notification_core_db import NotificationRequestLogDBModel


class NotificationRequestLogRepository:

    @classmethod
    async def log_new_notification_request(cls, event_id, request_id, channel, sent_to, source_identifier):
        log_data = {
            'event_id': event_id,
            'notification_request_id': request_id,
            'channel': channel,
            'sent_to': sent_to,
            'source_identifier': source_identifier
        }
        new_rows = await ORMWrapper.create(NotificationRequestLogDBModel, log_data)
        return new_rows

    @classmethod
    async def update_notification_request_log(cls, log_id, **kwargs):
        where = {'id': log_id}
        if log_id == '-1':
            operator_event_id = kwargs.pop("operator_event_id", None)
            if not operator_event_id:
                raise AssertionError("operator_event_id can not be None if `log_id` is `-1`")
            return await cls._update_notification_request_log_by_operator_event_id(operator_event_id, **kwargs)
        return await cls._update_notification_request_log(where, **kwargs)

    @classmethod
    async def _update_notification_request_log_by_operator_event_id(cls, operator_event_id, **kwargs):
        where = {'operator_event_id': operator_event_id}
        return await cls._update_notification_request_log(where, **kwargs)

    @classmethod
    async def _update_notification_request_log(cls, where, **kwargs):
        if kwargs.get('message'):
            kwargs['message'] = cls.truncate_value(kwargs['message'], 5000)
        if kwargs.get('metadata'):
            kwargs['metadata'] = cls.truncate_value(kwargs['metadata'], 5000)
        updated_rows = await ORMWrapper.update_with_filters(
            None, NotificationRequestLogDBModel, kwargs, where_clause=where
        )
        return updated_rows

    @classmethod
    async def update_notification_request_with_where_clause(cls, where_clause, **update_values):
        if update_values.get('message'):
            update_values['message'] = cls.truncate_value(update_values['message'], 5000)
        if update_values.get('metadata'):
            update_values['metadata'] = cls.truncate_value(update_values['metadata'], 5000)
        updated_rows = await ORMWrapper.update_with_filters(
            None, NotificationRequestLogDBModel, update_values, where_clause=where_clause
        )
        return updated_rows

    @classmethod
    async def get_notification_request_log(cls, limit=None, offset=None, order_by=None, **select_filters) -> [NotificationRequestLogDBModel]:
        olob = dict()
        if limit:
            olob["limit"] = limit
        if offset:
            olob["offset"] = offset
        if order_by:
            olob["order_by"] = order_by
        return await ORMWrapper.get_by_filters(NotificationRequestLogDBModel, filters=select_filters, **olob)

    @classmethod
    async def get_channel_status_analytics(cls, interval_hours=24):
        query = "select channel, status, count(*) as count from {} where created > now() - interval '{} hours' group by 1,2".format(DatabaseTables.NOTIFICATION_REQUEST_LOG.value, interval_hours)
        res = await ORMWrapper.raw_sql(query)
        return res

    @classmethod
    async def get_notification_request_log_count(cls, **select_filters) -> int:
        return await ORMWrapper.get_by_filters_count(NotificationRequestLogDBModel, filters=select_filters)

    @staticmethod
    def truncate_value(value, max_chars):
        if len(value) > max_chars:
            value = value[0:max_chars-5] + '.....'
        return value
