from typing import Optional
import logging

from tortoise_wrapper.wrappers import ORMWrapper

logger = logging.getLogger()


class BaseRepository:
    class Queries:
        GET_CALLBACK_DETAILS = """
select
  r.notification_request_id,
  r.source_identifier,
  r.sent_to,
  r.operator,
  r.operator_event_id,
  e.id as event_id,
  e.event_name,
  e.callback_enabled,
  a.name as app_name,
  a.callback_url,
  a.callback_events
from
  notification_request_log r
  join event e on r.event_id = e.id
  join app a on a.name = e.app_name
where
  {condition}
limit 1;
"""

    @classmethod
    async def get_log_details(
        cls, log_id: int, operator_event_id: Optional[str] = None
    ):
        query = cls.Queries.GET_CALLBACK_DETAILS
        condition = None
        values = []
        if operator_event_id:
            condition = "r.operator_event_id = $1"
            values = [str(operator_event_id)]
        else: # when log_id is not -1
            condition = "r.id = $1"
            values = [log_id]

        query = query.format(condition=condition)

        details = await ORMWrapper.raw_sql(query, values=values)
        if len(details) != 1:
            logger.error(
                "exactly one row was expected from the query with log_id %s and operator_event_id %s but received %s",
                log_id,
                operator_event_id,
                len(details),
            )
            raise AssertionError(
                f"Exactly one row was expected from the query but received {len(details)}"
            )
        return details[0]
