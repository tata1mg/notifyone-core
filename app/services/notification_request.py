import asyncio
from datetime import datetime, timedelta
import logging

from app.constants import NotificationChannels, NotificationRequestLogStatus
from app.models.notification_core import EventModel
from app.repositories.event import EventRepository
from app.utilities.utils import json_loads, async_gather_dict

from .email import EmailHandler
from .sms import SMSHandler
from .push import PushHandler
from .whatsapp import WhatsappHandler
from .logging import NotificationRequestLog


logger = logging.getLogger()


class NotificationRequest:

    @staticmethod
    def _transform_template_data(template_data):
        template_data = template_data or dict()
        template_data['current_datetime'] = (datetime.now() + timedelta(seconds=5.5 * 60 * 60)).strftime('%d-%m-%Y %H:%M:%S')
        template_data['current_date'] = (datetime.now() + timedelta(seconds=5.5 * 60 * 60)).strftime('%d-%m-%Y')

    @classmethod
    async def handle_notification_request_async(
        cls, request_body, subscriber_id, message_receive_count=1
    ):
        request_body = json_loads(request_body)
        results = await cls._handle_notification_request(
            request_body=request_body,
            message_receive_count=message_receive_count,
        )
        has_exception = any(res.unhandled_exception for res in results.values())
        return not has_exception

    @classmethod
    async def handle_notification_request_sync(cls, request_body, message_receive_count=1):
        result = await cls._handle_notification_request(
            request_body=request_body,
            message_receive_count=message_receive_count,
        )
        response = {'channels': {key: val.__dict__ for key, val in result.items()}}
        return response

    @classmethod
    async def _handle_notification_request(cls, request_body, message_receive_count=1):
        # request_body = V2PayloadParser.parse(request_body)
        app_name = request_body['app_name']
        event_name = request_body['event_name']
        event = await EventRepository.get_event(app_name, event_name)
        # Transform request body
        if request_body.get('body'):
            cls._transform_template_data(request_body['body'])

        # if message_receive_count > 1 (retry case), check and mute already triggered channels
        if message_receive_count > 1:
            # fetch notification request logs for the request_id in message
            # Filter out channels with status SUCCESS/INITIATED
            request_id = request_body['request_id']
            already_triggered_channels = await NotificationRequestLog.get_already_triggered_channels(request_id)
            event.mute_channels(already_triggered_channels)
        else:
            # Upsert template preview data
            # asyncio.create_task(LaraClient.upsert_event_preview_data(request_body))
            pass

        # log notification request in NEW status
        log_details = await NotificationRequestLog.log_notification_request(event, request_body)
        # run trigger limit check
        barred_channels = await cls.run_trigger_limit_check(event, request_body, log_details)
        # Get eligible channels
        active_channels = event.get_active_channels()
        eligible_channels = set(active_channels).difference(barred_channels)

        tasks = {}
        # Dispatch notification request to respective handlers
        for channel in eligible_channels:
            if channel == NotificationChannels.EMAIL.value:
                tasks.update({"email": EmailHandler.handle(event, request_body, log_details[channel])})
            elif channel == NotificationChannels.SMS.value:
                tasks.update({"sms": SMSHandler.handle(event, request_body, log_details[channel])})
            elif channel == NotificationChannels.WHATSAPP.value:
                tasks.update({"whatsapp": WhatsappHandler.handle(event, request_body, log_details[channel])})
            elif channel == NotificationChannels.PUSH.value:
                tasks.update({"push": PushHandler.handle(event, request_body, log_details[channel])})
        return await async_gather_dict(tasks, return_exceptions=True)

    @classmethod
    async def run_trigger_limit_check(cls, event: EventModel, request_body: dict, log_rows) -> list:
        barred_channels = list()
        if event.is_trigger_limit_enabled_for_any_active_channel():
            triggered_counts = await NotificationRequestLog.get_triggered_count_for_limit_check(event, request_body)
            active_channels = event.get_active_channels()
            for channel in active_channels:
                if event.is_trigger_limit_enabled_for_channel(channel) and event.triggers_limit[channel] < triggered_counts[channel]:
                    logger.info('Trigger limit breached. Event - {}, Channel - {}, Identifier - {}'.format(event.event_name, channel, NotificationChannels.get_source_identifier_for_event(request_body)))
                    barred_channels.append(channel)
                    asyncio.create_task(
                        NotificationRequestLog.update_notification_log(
                            log_rows[channel].id, status=NotificationRequestLogStatus.FAILED.value,
                            message="trigger limit breached")
                    )
        return barred_channels
