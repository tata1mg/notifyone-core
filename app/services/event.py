import json
import logging
from typing import Dict, Optional
from torpedo.exceptions import BadRequestException, NotFoundException
from app.manager.email_manager import EmailManager
from app.utilities.utils import validate_required_params, \
    get_default_actions, get_default_trigger_limits, check_format
from app.constants import ErrorMessages
from app.models.notification_core import EventModel
from app.repositories.event import EventRepository
from app.constants import NotificationChannels
from app.constants.constants import Event, EventType, Action
from app.constants.email import Email
from app.constants.event_priority import EventPriority
from app.exceptions import InvalidParamsException, ResourceConflictException
from app.manager.sms_manager import SmsManager, CreateSmsEvent
from app.manager.push_notification_manager import PushManager, CreatePushEvent
from app.manager.email_manager import CreateEmailEvent
from app.manager.event_manager import EventManager
from app.manager.whatsapp_manager import WhatsappManager,CreateWhatsappEvent
logger = logging.getLogger()

class Events:
    email_template_cache_version = 'email_template_cache_version'

    @classmethod
    async def get_events_custom(cls, attributes):
        for attr in attributes:
            if attr not in EventModel.attributes_available_to_fetch():
                raise BadRequestException(ErrorMessages.INVALID_EVENT_ATTRIBUTE.value)

        all_events = await EventRepository.get_events()
        return [event.custom_dict(attributes) for event in all_events]
    
    @classmethod
    def get_event_actions(cls, data):
        """
        This function is used to get event's actions.
        :param data: dict containing different event's field.
        """
        actions = {}
        actions = CreateSmsEvent.prepare_event_actions(data=data)
        actions |= CreateEmailEvent.prepare_event_actions(data=data)
        actions |= CreateWhatsappEvent.prepare_event_actions(data=data)
        actions |= CreatePushEvent.prepare_event_actions(data=data)
        return actions
    
    @classmethod
    async def get_event_data(cls, data: dict, event_actions: Optional[Dict] = None, event_id: Optional[int] = None,
                             creating_event: Optional[bool] = False):
        """
        This function  is used to get event data
        :param data: dict containing different event's field.
        :return: dict of event data
        """
        actions = cls.get_event_actions(data=data)
        event_data = {}
        if creating_event:
            event_actions = get_default_actions()

        app_name = data.get(Event.APP_NAME)
        event_name = data.get(Event.EVENT_NAME)
        user_email = data.get(Event.USER_EMAIL)

        if actions.get(NotificationChannels.EMAIL.value) and isinstance(
                actions.get(NotificationChannels.EMAIL.value), dict):
            event_data[NotificationChannels.EMAIL.value] = await CreateEmailEvent.get_data_for_event(
                actions.get(NotificationChannels.EMAIL.value), app_name, event_name, user_email, event_id)
            event_actions[NotificationChannels.EMAIL.value] = Action.ON.value

        if actions.get(NotificationChannels.SMS.value) and isinstance(
                actions.get(NotificationChannels.SMS.value), dict):
            event_data[NotificationChannels.SMS.value] = await CreateSmsEvent.get_data_for_event(
                actions.get(NotificationChannels.SMS.value), user_email, event_id)
            event_actions[NotificationChannels.SMS.value] = Action.ON.value

        if actions.get(NotificationChannels.PUSH.value) and isinstance(
                actions.get(NotificationChannels.PUSH.value), dict):
            event_data[NotificationChannels.PUSH.value] = await CreatePushEvent.get_data_for_event(
                actions.get(NotificationChannels.PUSH.value), user_email, event_id)
            event_actions[NotificationChannels.PUSH.value] = Action.ON.value

        if actions.get(NotificationChannels.WHATSAPP.value) and isinstance(
                actions.get(NotificationChannels.WHATSAPP.value), dict):
            event_data[NotificationChannels.WHATSAPP.value] = await CreateWhatsappEvent.get_data_for_event(
                actions.get(NotificationChannels.WHATSAPP.value), user_email, event_id)
            event_actions[NotificationChannels.WHATSAPP.value] = Action.ON.value
            # not checking other event type (i.e, call)
        # in action because already they are restricted in getting action from payload.
        if not event_data:
            raise BadRequestException(ErrorMessages.EMPTY_ACTION_ERROR.value)
        return event_data, event_actions

    @classmethod
    async def validate_event_existence(cls, event_name, app_name):
        """
        This function is used to validate if event already created or not .
        :param event_name: name of the event.
        :param app_name: app name of event.
        :return: None
        """
        event = await EventRepository.get_event_from_db(
                event_name=event_name, app_name=app_name)
        if event:
            raise ResourceConflictException(
                ErrorMessages.EVENT_ALREADY_CREATED_ERROR.value.format(
                    event_name, app_name))

    @staticmethod
    def _validate_payload(payload, required_params, creating_event=False):
        """
        This is used to validate payload received for creating
        events or adding actions to existing events.
        :param payload: payload dict
        :param required_params: list of required_params.
        :param creating_event : flag for checking if creating event or adding action.
        """
        validate_required_params(payload=payload,required_params=required_params)
        check_format(payload.get('app_name'))  
        check_format(payload.get('event_name'))                       
        if creating_event:
            # this is used to validate priority of event.
            priority = payload.get(Event.EVENT_PRIORITY)
            if priority not in [EventPriority.HIGH.value, EventPriority.LOW.value, EventPriority.MEDIUM.value, EventPriority.CRITICAL.value]:
                raise InvalidParamsException(f'{priority} is not a valid event priority')
            
            # this is used to validate event_type of event
            event_type = payload.get(Event.EVENT_TYPE)
            if event_type not in [EventType.PROMOTIONAL.value, EventType.TRANSACTIONAL.value, EventType.OTHER.value ]:
                raise InvalidParamsException(f'{event_type} is not a valid event type')    

    @classmethod
    async def create_event(cls,data):
        """
        This function is used to create new events.
        :param data: dict containing different required event's field.
        :return: None
        """
        cls._validate_payload(
            payload=data,
            required_params=Event.CREATE_EVENT_REQUIRED_PARAMS,
            creating_event=True,
        ) 

        await cls.validate_event_existence(
            event_name=data['event_name'], app_name=data['app_name'])
        trigger_limit = get_default_trigger_limits()
        event_data, event_actions = await cls.get_event_data(data=data, creating_event=True)
        event_details = {
            'event_name': data.get('event_name'),
            'app_name': data.get('app_name'),
            'actions': json.dumps(event_actions),
            'subject': event_data.get('email', {}).get(Email.SUBJECT, ''),
            'triggers_limit': json.dumps(trigger_limit),
            'event_type': data.get('event_type'),
            'meta_info': json.dumps({Event.EVENT_PRIORITY: data.get(Event.EVENT_PRIORITY)}),
            'updated_by': data.get('user_email'),
            'is_deleted': Event.SOFT_DELETE_DEFAULT_VALUE
        }
        row = await EventRepository.create_event(
            event_details=event_details)
        event_id = row.id        
        await cls.__create_post_event_data_entry(event_data=event_data, event_id=event_id)
        logger.info(
            Event.NEW_EVENT_CREATED_MESSAGE.format(
                event_name=data['event_name'],
                app_name=data['app_name'],
                user_email=data['user_email']))
        result = {
            'event_id':row.id,
            'event_name':row.event_name,
            'app_name': row.app_name,
            'action': row.actions,
            'trigger_limit': row.triggers_limit,
            'created_by': data.get('user_email')
        } 
        return result       
     
    @classmethod
    async def add_new_action_to_event(cls, data):
        """
        This function is used to add new action i.e, sms or email etc. to event.
        :param data: dict containing different event's field.
        :return: None
        """
        cls._validate_payload(
            payload=data,
            required_params=Event.ADD_ACTION_REQUIRED_PARAMS
        )
        event_detail = await cls.get_event_details(
            event_name=data['event_name'], app_name=data['app_name'])
        event_id = event_detail.get('id')
        event_actions = event_detail.get('actions')
        event_data, event_actions = await cls.get_event_data(data=data, event_actions=event_actions, event_id=event_id)
        values = {'updated_by': data.get('user_email'), 'actions': json.dumps(event_actions)}
        await EventRepository.update_event(app_name=data['app_name'],
                                           event_name=data['event_name'],
                                           values=values)
        await cls.__create_post_event_data_entry(event_data=event_data, event_id=event_id)
        logger.info(
            Event.NEW_ACTION_ADDED_MESSAGE.format(
                event_name=data['event_name'],
                app_name=data['app_name'],
                user_email=data['user_email']))
        result = await EventRepository.get_event_details(app_name=data['app_name'], event_name=data['event_name'])
        return result

    @classmethod
    async def __create_post_event_data_entry(cls, event_data, event_id):
        """
        This function is used to create different event's types data entries,
        after creating event in DB if required.
        For example, it creates email entries in the email content table,
        after creating its event in event table
        similarly,if required for other event types.
        :param event_data : Dict containing data of event types that require post-event creation entry.
        :param event_id : id of the event created.
        """
        if event_data.get('email'):
            await CreateEmailEvent.create_post_event_entry(email=event_data.get('email'), event_id=event_id)
        if event_data.get('sms'):    
            await CreateSmsEvent.create_post_event_entry(sms=event_data.get('sms'), event_id=event_id)
        if event_data.get('push'):    
            await CreatePushEvent.create_post_event_entry(push=event_data.get('push'), event_id=event_id)
        if event_data.get('whatsapp'):
            await CreateWhatsappEvent.create_post_event_entry(whatsapp=event_data.get('whatsapp'), event_id=event_id)            
    
    @staticmethod
    async def get_event_details(event_name: str, app_name: str):
        """
        This is used fo getting event details.
        :param event_name: name of the event
        :param app_name: app name of event.
        """
        event_detail = await EventRepository.get_event_from_db(event_name=event_name, app_name=app_name)
        if event_detail :
            return event_detail
        else :
             raise BadRequestException(f"event is not exists for event name:{event_name} and app name:{app_name}")    

    @classmethod
    async def get_event (cls, event_id:Optional[int] =None , channel_name: Optional[str] =None, query_params:Optional[Dict] =None):
        """
        This is used fo getting event details.
        :param event_id: id of the event
        :param channel: channel name of event.
        """
        if channel_name and channel_name == NotificationChannels.EMAIL.value:
           data= await EmailManager.filter_email(event_id, query_params)
           return data
        if channel_name and channel_name == NotificationChannels.SMS.value:
           data= await SmsManager.filter_sms(event_id, query_params)
           return data
        if channel_name and channel_name == NotificationChannels.PUSH.value:
           data= await PushManager.filter_push_notification(event_id, query_params)
           return data 
        if channel_name and channel_name == NotificationChannels.WHATSAPP.value:
            data= await WhatsappManager.filter_whatsapp(event_id, query_params)
            return data
        return await EventManager.get_all_events(event_id=event_id)    

    @classmethod
    async def get_events(cls, request_args):
        query_params = {}
        size= request_args.get('size')
        start= request_args.get('start')
        if size:
            query_params.update({'size':size})
        if start:
            query_params.update({'start':start})
        if request_args.get('app_name'):
            app_name = request_args.get('app_name')
            query_params.update({'app_name':app_name})
        if request_args.get('event_name'):
            event_name = request_args.get('event_name')
            query_params.update({'event_name':event_name})
        if request_args.get('channel'):
            channel = request_args.get('channel')
            query_params.update({'channel':channel})
            return await cls.get_event(channel_name=channel, query_params=query_params)

        return await EventManager.get_all_events(query_params=query_params) 
    
    @classmethod
    async def delete_event(cls, event_id: int , user_email: str):
        event = await EventRepository.get_events_by_id(event_id)
        if event and event.is_deleted == False:
            values = {'is_deleted': True,
                    'updated_by':user_email}            
            await EventRepository.update_event_with_id( event_id , values)
            return {"message": "event has been deleted sucessfully"} 
        else:
            raise NotFoundException('event is not found') 
