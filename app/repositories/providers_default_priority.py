from tortoise.exceptions import IntegrityError
from torpedo.exceptions import NotFoundException, BadRequestException
from tortoise_wrapper.wrappers import ORMWrapper

from app.constants import NotificationChannels, ProvidersDefaultPriorityStatus
from app.models.notification_core_db import ProvidersDefaultPriorityDBModel


class ProvidersDefaultPriorityRepository:

    @classmethod
    async def get_channel_priority(cls, channel: NotificationChannels) -> ProvidersDefaultPriorityDBModel:
        select_filter = {
            "channel": channel.value
        }
        rows = await ORMWrapper.get_by_filters(ProvidersDefaultPriorityDBModel, select_filter)
        if not rows:
            raise NotFoundException("No priority found")
        return rows[0]

    @classmethod
    async def add_new_priority(cls, channel: NotificationChannels, priority: list):
        values = {
            "channel": channel.value,
            "priority": priority
        }
        try:
            await ORMWrapper.create(ProvidersDefaultPriorityDBModel, values)
        except IntegrityError:
            raise BadRequestException("Default priority for channel {} already present".format(channel.value))
        return await cls.get_channel_priority(channel)

    @classmethod
    async def update_priority(cls, channel: NotificationChannels, disable=False, priority: list=None):
        values = {
            "status": ProvidersDefaultPriorityStatus.DISABLED.value if disable else ProvidersDefaultPriorityStatus.ACTIVE.value
        }
        if priority is not None:
            values["priority"] = priority

        where_clause = {
            "channel": channel.value
        }
        await ORMWrapper.update_with_filters(None, ProvidersDefaultPriorityDBModel, values, where_clause=where_clause)
        return await cls.get_channel_priority(channel)
