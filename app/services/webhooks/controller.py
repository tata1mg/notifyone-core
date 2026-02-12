from typing import Dict, Optional

import logging
import json

from torpedo.common_utils import CONFIG
from app.service_clients.base_api_client import APIClient

from app.constants.notification_channels import NotificationChannels
from app.constants.status import ExecutionDetailsSource, ExecutionDetailsEventStatus
from app.repositories.base import BaseRepository

config = CONFIG.config
logger = logging.getLogger()


class WebhookController:
    @staticmethod
    async def _fetch_callback_details(
        channel: NotificationChannels,
        log_id: int,
        operator_event_id: Optional[str] = None,
    ):
        details = await BaseRepository.get_log_details(
            log_id=int(log_id), operator_event_id=operator_event_id
        )
        callback_enabled = details.pop("callback_enabled", False)
        callback_events = details.pop("callback_events", {})
        return (
            details,
            callback_enabled,
            json.loads(callback_events).get(channel.value),
        )

    @staticmethod
    def __create_payload(
        status: str, timestamp: str, channel: NotificationChannels, details: Dict
    ):
        return {
            "status": status,
            "timestamp": timestamp,
            "channel": channel.value,
            "event": {
                "id": details.get("event_id"),
                "name": details.get("event_name"),
                "app_name": details.get("app_name"),
            },
            "recipient": details.get("sent_to"),
            "source_identifier": details.get("source_identifier"),
            "request_id": details.get("notification_request_id"),
            "details": {
                "operator": details.get("operator"),
                "operator_event_id": details.get("operator_event_id"),
            },
        }

    @staticmethod
    def _should_send_callback(
        attempt_number: int,
        channel: NotificationChannels,
        source: ExecutionDetailsSource,
        status: ExecutionDetailsEventStatus,
    ):
        if source == ExecutionDetailsSource.WEBHOOK:
            return True

        is_success = source == ExecutionDetailsSource.INTERNAL and status == (
            ExecutionDetailsEventStatus.QUEUED or ExecutionDetailsEventStatus.SUCCESS
        )

        max_attempts = config.get("MAX_ATTEMPTS", {})
        # check for attempt_number + 1 as attempt_number is 0 indexed
        is_last_attempt = (attempt_number + 1) >= max_attempts.get(
            str(channel.value).upper()
        )
        return is_success or is_last_attempt

    @classmethod
    async def handle_webhook(
        cls,
        log_id: int,
        status: str,
        source: str,
        channel: str,
        timestamp: str,
        channel_status: str,
        attempt_number: int,
        operator_event_id: int = None,
    ):
        channel = NotificationChannels(channel)
        try:
            if not cls._should_send_callback(
                channel=channel,
                attempt_number=attempt_number,
                source=ExecutionDetailsSource(source),
                status=ExecutionDetailsEventStatus(status),
            ):
                logger.info(
                    "Not sending callback as this is not the final attempt for "
                    "log_id %s operator_event_id %s",
                    log_id,
                    operator_event_id,
                )
                return

            (
                details,
                callback_enabled,
                allowed_events,
            ) = await cls._fetch_callback_details(
                channel,
                log_id,
                operator_event_id,
            )

            notification_status = channel_status or status
            if not callback_enabled or notification_status not in allowed_events:
                logger.info(
                    "Callback not enabled for the given status %s or event %s. Skipping for log_id %s operator_event_id %s",
                    notification_status,
                    details.get("event_name"),
                    log_id,
                    operator_event_id,
                )
                return

            payload = cls.__create_payload(
                notification_status, timestamp, channel, details
            )
            url = details.get("callback_url")

            logger.info("sending POST request to url %s with payload %s", url, payload)
            await APIClient.post(
                url, data=payload, headers={"Content-Type": "application/json"}
            )
        except Exception as err:
            logger.error(
                "Encountered error while handling webhook for  log_id %s operator_event_id %s: %s",
                log_id,
                operator_event_id,
                err,
            )
