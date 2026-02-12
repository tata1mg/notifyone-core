from typing import List, Callable
import logging
from torpedo import CONFIG
from app.constants import (
    NotificationChannels,
    NotificationRequestLogStatus,
    ErrorMessages,
    VariableMappingKeys, 
)
from app.exceptions import NoSendAddressFoundException
from app.models.notification_core import EventModel
from app.service_clients.publisher import PublishResult
from app.utilities import (
    dispatch_notification_request_common_payload,
    is_notification_allowed_for_mobile,
    utils
)
from .abstract_handler import AbstractHandler
from .logging import NotificationRequestLog
from app.repositories.whatsapp_content import WhatsappContentRepository
logger = logging.getLogger()

class WhatsappHandler(AbstractHandler):
    _dispatch_notification_config = CONFIG.config["DISPATCH_NOTIFICATION_REQUEST"]
    _channel_config = _dispatch_notification_config["WHATSAPP"]

    @classmethod
    async def handle(
        cls, event: EventModel, request_body, notification_request_log_row
    ):
        # TODO Push to SNS
        # TODO Update analytics log
        unhandled_exception = False
        status = NotificationRequestLogStatus.INITIATED
        message = None
        template = None
        body_values = None
        try:
            send_address = NotificationChannels.get_sent_to_for_channel(
                NotificationChannels.WHATSAPP.value, request_body
            )
            if not send_address:
                raise NoSendAddressFoundException(
                    ErrorMessages.NO_SEND_ADDRESS_FOUND.value
                )
            
            if not is_notification_allowed_for_mobile(send_address):
                raise NoSendAddressFoundException(
                    ErrorMessages.SEND_ADDRESS_NOT_ALLOWED_ON_TEST_ENV.value
                )

            request_body = request_body or dict()
            phone_number = send_address
            whatsapp_body = request_body.get("whatsapp")
            body_values = whatsapp_body.get("body_values", [])
            header_values = whatsapp_body.get("header_values", [])
            button_values = whatsapp_body.get("button_values", {})
            attachments = request_body.get("attachments")
            data = dispatch_notification_request_common_payload(
                event.id,
                event.event_name,
                event.app_name,
                NotificationChannels.WHATSAPP.value,
                notification_request_log_row.id,
            )
            whatsapp_data = (
                await WhatsappContentRepository.get_whatsapp_content_from_event_id(event.id)
            )
            template = whatsapp_data.name
            if not body_values:
                body_values = cls.get_field_values(request_body.get('body'), whatsapp_data.variable_mapping, VariableMappingKeys.BODY)
            if not button_values:
                button_values = cls.get_field_values(request_body.get('body'), whatsapp_data.variable_mapping, VariableMappingKeys.BUTTON, False)
            if not header_values:
                header_values = cls.get_field_values(request_body.get('body'), whatsapp_data.variable_mapping, VariableMappingKeys.HEADER)
            data.update(
                {
                    "template": template,
                    "body_values": body_values,
                    "header_values": header_values,
                    "button_values": button_values,
                    "mobile": phone_number,
                }
            )
            if attachments:
                data.update(
                    {
                        "attachment_data": {
                            "attachments": attachments,
                            "filename": request_body.get("filename"),
                        }
                    }
                )
            result = await cls._dispatch_notification.publish(
                payload=data, priority=event.priority
            )
        except NoSendAddressFoundException as ne:
            status = NotificationRequestLogStatus.NOT_ELIGIBLE
            message = str(ne)
            result = PublishResult(is_success=False, status=status, message=message)
        except Exception as e:
            status = NotificationRequestLogStatus.FAILED
            message = str(e)
            result = PublishResult(is_success=False, status=status, message=message)
            result.unhandled_exception = True
            logger.exception(e)
        finally:
            # update notification request log status
            await NotificationRequestLog.update_notification_request_processed_status(
                notification_request_log_row.id,
                message=result.message,
                status=result.status.value,
                content=cls._get_content(template, body_values, header_values, button_values),
                channel=NotificationChannels.WHATSAPP,
                request_id=request_body["request_id"],
            )
        if unhandled_exception:
            raise Exception("Unhandled exception in sending push")
        return result

    @classmethod
    def _get_content(self, template: str, body_values: List[str], header_values: List[str], button_values:dict):
        return f"templateName: {template}\nBodyValues: {body_values}\nHeaderValues: {header_values}\nButtonValues: {button_values}"

    @classmethod
    async def get_whatsapp_content(cls, event: EventModel, _body: dict):
        whatsapp_content = WhatsappContentRepository.get_whatsapp_content_from_event_id(event.id)
        whatsapp_data = {
            'name': whatsapp_content.name,
            'variable_mapping': whatsapp_content.variable_mapping,
        }
        return whatsapp_data

    @classmethod
    def get_field_values(cls, body: dict, variable_mapping: dict, type: str=VariableMappingKeys.BODY, return_list: bool = True):
        """
        variable_mapping = {'body': {'var1': 1, 'var2': [2, 4], 'a.b.var3': 3}}
        body = {'var1': 'value', 'var2': 'value', 'a': {'b': {'var3': 'value'}}}

        The method creates a list of values in the order of variable_mapping and gives a list or a dic in response
        response = {'0':['value1', 'value2'], '1':['value2'], '2', 'value3']}/['value1', 'value2', 'value3', 'value2']
        """
        if not variable_mapping:
            return [] if return_list else {}

        variables = variable_mapping.get(type.value)

        if not variables:
            return [] if return_list else {}

        if return_list:
            values = cls._get_values(
                variables, body, lambda x: x, lambda x: x - 1
            )
        else:
            values = cls._get_values(
                variables, body, lambda x: [x], lambda x: str(x - 1)
            )

        if return_list:
            maxlen = utils.get_max(variables.values())
            values_list = [None] * maxlen

            for idx, value in values.items():
                values_list[idx] = value

            return values_list

        return values

    @classmethod
    def _get_values(
        cls,
        variable_mapping: dict,
        body: dict,
        value_transform: Callable,
        key_transform: Callable,
    ):
        values = {}
        for key, indexes in variable_mapping.items():
            keys = key.split(".")
            value = body

            for k in keys:
                value = value.get(k)
                if value is None:
                    break

            if value is not None:
                value = value_transform(value)

                if isinstance(indexes, list):
                    for idx in indexes:
                        key = key_transform(idx)
                        values[key] = value
                elif isinstance(indexes, int):
                    key = key_transform(indexes)
                    values[key] = value

        return values