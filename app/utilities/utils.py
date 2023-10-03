from typing import Any, Awaitable, Dict, Tuple
import asyncio
import datetime
import json
import time
from contextlib import suppress
from concurrent import futures
import os
import re
import sys
import uuid
from torpedo import CONFIG
from app.exceptions import RequiredParamsException
from app.constants.constants import Event
from .drivers import CustomJinjaEnvironment
from app.constants.constants import Action, TriggerLimit
from app.constants import NotificationChannels

def generate_uuid():
    return str(uuid.uuid4())

def json_dumps(data):
    return json.dumps(data)

def json_loads(data_str):
    return json.loads(data_str)

def max_int():
    return sys.maxsize

def does_file_exists(path: str):
    return os.path.exists(path)

def delete_file(path: str):
    if does_file_exists(path):
        with suppress(Exception):
            os.remove(path)

async def run_in_thread(func_to_call, *args, **kwargs):
    with futures.ThreadPoolExecutor(max_workers=1) as executor:
        job = executor.submit(func_to_call, *args, **kwargs)
        return await asyncio.wrap_future(job)

def write_file(path: str, content, mode: str=None, encoding: str=None):
    mode = mode or 'w+'
    encoding = encoding or 'utf-8'
    with open(path, mode=mode, encoding=encoding) as file:
        file.write(content)

async def write_file_async(path: str, content, mode: str = None, encoding: str = None):
    await run_in_thread(write_file, path, content, mode, encoding)

async def render_text(message, data):
    return await CustomJinjaEnvironment.render_text_async(message, data)

async def get_transformed_message_by_text(text: str, data: dict):
    message_body = await CustomJinjaEnvironment.render_text_async(text, data)
    return message_body

def get_project_root_path():
    path = os.path.abspath(__file__)
    path = path.replace('/utilities/utils.py', '')
    project_root = os.path.dirname(path)
    return project_root

def dispatch_notification_request_common_payload(event_id, event_name, app_name, channel, notification_log_id) -> dict:
    return {
        'event_id': event_id,
        'event_name': event_name,
        'app_name': app_name,
        'notification_channel': channel,
        'notification_log_id': notification_log_id
    }


def current_utc_timestamp():
    return datetime.datetime.utcnow()


def current_epoch():
    return int(time.time()*1000)


def is_notification_allowed_for_email(email: str) -> bool:
    test_allowed_emails = CONFIG.config.get('TEST_ALLOWED_EMAILS') or list()
    if not is_testing_environment():
        return True

    for email in email.split(','):
        if email not in test_allowed_emails:
            return False
    return True

def is_notification_allowed_for_mobile(mobile: str):
    test_allowed_mobiles = CONFIG.config.get('TEST_ALLOWED_MOBILES') or list()
    if is_testing_environment() and mobile not in test_allowed_mobiles:
        return False
    return True

def is_testing_environment() -> bool:
    return 'TEST_ENVIRONMENT' in CONFIG.config and CONFIG.config['TEST_ENVIRONMENT'] is True

def validate_required_params(payload: dict, required_params: list):
    """
    This function is used to validate the required_param's existence in the payload.
    :param payload: dict containing different event's field.
    :param required_params: list of required params .
    :return: None
    """
    missing_parms = []
    for param in required_params:
        if not payload.get(str(param)):
            missing_parms.append(param)
    if missing_parms:
        raise RequiredParamsException(
            'Following params: {} missing in payload'.format(",".join(missing_parms)))


def get_event_unique_identifier(event_name: str, app_name: str) -> str:
    """
    This function is used to get unique identifier of any event across Notification service.
    :param event_name: name of the event
    :param app_name: source from which this event will be triggered.
    :return: unique_identifier
    """
    return Event.KEY_DELIMITER.join([event_name, app_name])

def get_email_content_path(unique_identifier: str) -> str:
    """
    This function is used to get sample email content for an event .
    :param unique_identifier: identifier of the event
    :return: path
    """
    return '/opt/1mg/lara_service/lara/template/' + unique_identifier + '.jade'

def is_email_valid(email: str):
    """
    This function is used to check if email is valid or not.
    :param email: email ID
    :return: True/False
    """
    email_format = re.compile(
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"'
        r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,10}\.?$',
        re.IGNORECASE)
    if email_format.match(email):
        return True
    return False         

def query_filters(query_params:dict ={}):
    where =''
    for key , value in query_params.items():
        if key=='app_name' and query_params.get(key):
                where += ''' and event.app_name = '{value}' '''.format(value=value)
        if key =='event_name' and query_params.get(key):
                where += ''' and event.event_name = '{value}' '''.format(value=value)    
    return where                

def get_default_actions() -> dict:
    """
    This function is used for getting deactivated actions Dict.
    :return: actions dict
    """
    # deactivating all event type at time of creation later it can be activated from CAD UI
    actions = {
        NotificationChannels.EMAIL.value: Action.OFF.value,
        NotificationChannels.SMS.value: Action.OFF.value,
        NotificationChannels.WHATSAPP.value: Action.OFF.value,
        NotificationChannels.PUSH.value: Action.OFF.value,
    }
    return actions

def get_default_trigger_limits() -> dict:
    """
    This function is used for getting default trigger limits Dict.
    :return: trigger limit dict
    """
    # making trigger limit of all event type 's to 1 as later it can be changes from CAD UI.
    trigger_limit = {
        NotificationChannels.EMAIL.value: TriggerLimit.SINGLE.value,
        NotificationChannels.SMS.value: TriggerLimit.SINGLE.value,
        NotificationChannels.WHATSAPP.value: TriggerLimit.SINGLE.value,
        NotificationChannels.PUSH.value: TriggerLimit.SINGLE.value
    }
    return trigger_limit

def current_epoch_in_millis():
    return int(time.time()*1000)

def check_format(value):
    if not re.match("^[a-zA-Z_]+$", value):
        raise RequiredParamsException("event name and app name should not contain any special character or any numerical value")

async def async_gather_dict(tasks: Dict[str, Awaitable[str]], **kwargs: Dict[str, Any]) -> Dict[str, str]:
    async def mark(key: str, coro: Awaitable[str]) -> Tuple[str, str]:
        return key, await coro

    return {
        key: result
        for key, result in await asyncio.gather(
            *(mark(key, coro) for key, coro in tasks.items()), **kwargs
        )
    }