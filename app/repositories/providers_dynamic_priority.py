from tortoise.exceptions import IntegrityError
from torpedo.exceptions import NotFoundException, BadRequestException
from tortoise_wrapper.wrappers import ORMWrapper

from app.constants import NotificationChannels, ProvidersDynamicPriorityStatus
from app.models.notification_core_db import ProvidersDynamicPriorityDBModel


class ProvidersDynamicPriorityRepository:

    @classmethod
    async def get_channel_priority(cls, channel: NotificationChannels) -> ProvidersDynamicPriorityDBModel:
        select_filter = {
            "channel": channel.value
        }
        rows = await ORMWrapper.get_by_filters(ProvidersDynamicPriorityDBModel, select_filter)
        if not rows:
            raise NotFoundException("No priority found")
        return rows[0]

    @classmethod
    async def add_new_priority(cls, channel: NotificationChannels, priority_logic: str):
        values = {
            "channel": channel.value,
            "priority_logic": priority_logic
        }
        try:
            await ORMWrapper.create(ProvidersDynamicPriorityDBModel, values)
        except IntegrityError:
            raise BadRequestException("Default priority for channel {} already present".format(channel.value))
        return await cls.get_channel_priority(channel)

    @classmethod
    async def update_priority(cls, channel: NotificationChannels, disable=False, priority_logic: str = None):
        values = {
            "status": ProvidersDynamicPriorityStatus.DISABLED.value if disable else ProvidersDynamicPriorityStatus.DISABLED.value
        }
        if priority_logic is not None:
            values["priority_logic"] = priority_logic

        where_clause = {
            "channel": channel.value
        }
        await ORMWrapper.update_with_filters(None, ProvidersDynamicPriorityDBModel, values, where_clause=where_clause)
        return await cls.get_channel_priority(channel)
