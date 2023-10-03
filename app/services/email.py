import logging
import os
import textwrap
import random
from typing import Optional
from torpedo import CONFIG
from torpedo.exceptions import BadRequestException
from app.constants import NotificationChannels, NotificationRequestLogStatus, Email, ErrorMessages
from app.exceptions import NoSendAddressFoundException, AppNotConfigured
from app.utilities.drivers import CustomJinjaEnvironment
from app.models.notification_core import EventModel, EmailContentModel, AppsModel
from app.repositories.email_content import EmailContentRepository
from app.repositories.apps import AppsRepository
from app.utilities import does_file_exists, run_in_thread, utils, write_file_async, get_project_root_path, \
    dispatch_notification_request_common_payload, is_notification_allowed_for_email, current_epoch
from app.caches import NotificationCoreCache
from app.service_clients.publisher import PublishResult
from .abstract_handler import AbstractHandler
from .logging import NotificationRequestLog
from app.constants import EventPriority

logger = logging.getLogger()
project_root = get_project_root_path()
""""""
class EmailHandler(AbstractHandler):

    _dispatch_notification_config = CONFIG.config['DISPATCH_NOTIFICATION_REQUEST']
    _channel_config = _dispatch_notification_config['EMAIL']
    email_template_cache_version = 'email_template_cache_version'

    include_start = '$include_start-'
    include_end = '-$include_end'

    _existing_files = dict()

    @classmethod
    async def handle(cls, event: EventModel, request_body, notification_request_log_row):
        # TODO check for invalid email ID (this is being stored in a redis set in lara | Skipping for now, requirement
        #  analysis to be done first before implementing the same here. Redis set contains just 2 emails as of now.)
        # TODO Push to SNS
        # TODO Update analytics log
        unhandled_exception = False
        status = NotificationRequestLogStatus.INITIATED
        message = None
        email_body = None
        try:

            send_address = NotificationChannels.get_sent_to_for_channel(NotificationChannels.EMAIL.value, request_body)

            if not send_address:
                raise NoSendAddressFoundException(ErrorMessages.NO_SEND_ADDRESS_FOUND.value)

            # Currently, we support only one email id in send_address
            send_address = send_address[0]

            if not is_notification_allowed_for_email(send_address):
                raise NoSendAddressFoundException(ErrorMessages.SEND_ADDRESS_NOT_ALLOWED_ON_TEST_ENV.value)

            app = await AppsRepository.get_app_by_name(event.app_name)
            if not app:
                raise AppNotConfigured(ErrorMessages.APP_NOT_CONFIGURED.value)

            email_subject, email_body = await cls.get_email_subject_and_body(event, request_body)
            data = dispatch_notification_request_common_payload(
                event.id, event.event_name, event.app_name, NotificationChannels.EMAIL.value,
                notification_request_log_row.id
            )
            email_channel_data = request_body["channels"]["email"]
            attachments = request_body['attachments']
            result = await cls.publish(app, email_channel_data, data, send_address, email_subject, email_body, attachments=attachments, priority=event.priority)
        except NoSendAddressFoundException as ne:
            status = NotificationRequestLogStatus.NOT_ELIGIBLE
            message = str(ne)
            result = PublishResult(
                is_success=False, status=status, message=message
            )
        except AppNotConfigured as ane:
            status = NotificationRequestLogStatus.NOT_ELIGIBLE
            message = str(ane)
            result = PublishResult(
                is_success=False, status=status, message=message
            )
        except Exception as e:
            status = NotificationRequestLogStatus.FAILED
            message = str(e)
            result = PublishResult(
                is_success=False, status=status, message=message
            )
            result.unhandled_exception = True
            logger.exception(e)
        finally:
            # update notification request log status
            await NotificationRequestLog.update_notification_request_processed_status(
                notification_request_log_row.id, 
                message=message,
                status=status.value,
                content=email_body,
                channel=NotificationChannels.EMAIL,
                request_id=request_body['request_id'],
            )
        return result

    @classmethod
    async def publish(cls, app: AppsModel, email_channel_data, data, recipient, subject, body, attachments=None, priority:EventPriority = EventPriority.LOW):
        cc = email_channel_data.get('cc')
        bcc = email_channel_data.get('bcc')
        sender = {
            'reply_to': email_channel_data.get('reply_to') or app.email.reply_to,
            'name': email_channel_data.get('sender', {}).get('name') or app.email.sender.name,
            'address': email_channel_data.get('sender', {}).get('address') or app.email.sender.address
        }
        data.update({
            'subject': subject,
            'message': body,
            'to': recipient,
            'files': attachments,
            'cc': cc,
            'bcc': bcc,
            'sender': sender
        })
        return await cls._dispatch_notification.publish(payload=data, priority=priority)
    
    @classmethod
    async def get_email_subject_and_body(cls, event: EventModel, request_body: dict):
        email_body, raw_subject = await cls.get_email_details(event, request_body['body'])
        email_channel_data = request_body["channels"]["email"]
        subject = email_channel_data.get('subject') or raw_subject or ''
        subject = await CustomJinjaEnvironment.render_text_async(subject, request_body['body'])
        return subject, email_body

    @classmethod
    async def get_email_details(cls, event: EventModel, data: dict):
        email_content = await EmailContentRepository.get_email_content_from_event_id(event.id)
        # Future Scope : Handle support for Multiple templates
        if email_content:
            email_body, subject = await cls.get_email_details_from_db(data, email_content)
        else:
            template = '{}_{}'.format(event.event_name, event.app_name)
            subject = event.subject
            email_body = await cls.get_email_details_from_file(template, data)
        return email_body, subject

    @classmethod
    async def get_email_details_from_db(cls, data: dict, email_content_template: EmailContentModel):
        # Handle htmls here also
        template_id, content = email_content_template.id, email_content_template.content
        if cls.is_content_html(content):
            email_body = await CustomJinjaEnvironment.render_text_async(content, data)
        else:
            extension = 'jade'
            filename = cls.get_filename(template_id, extension)
            prefix_path, directory = cls.get_db_files_path()
            file_path = os.path.join(prefix_path, filename)
            # get latest template version
            latest_template_version = await cls.get_latest_email_template_version()
            file_exists = cls.check_file_in_cache(file_path, latest_template_version)
            if file_exists:
                email_body = await cls.get_email_details_from_file(os.path.join(directory, filename), data)
            else:
                logger.info('File path not found for template_id {}'.format(template_id))
                email_body = await cls.get_email_body_from_template_content(email_content_template, data)
        subject = email_content_template.subject
        return email_body, subject
    
    @classmethod
    async def handle_email_template_update(cls, latest_template_version):
        """
        upsert new template version
        """
        await NotificationCoreCache.set_key(cls.email_template_cache_version, str(latest_template_version))

    @classmethod
    async def get_latest_email_template_version(cls):
        version = await NotificationCoreCache.get_key(cls.email_template_cache_version)
        version = version or str(current_epoch())
        return version

    @classmethod
    async def get_email_body_from_template_content(cls, email_content_template: EmailContentModel, data: dict):
        all_email_content_map = await cls.get_all_email_content_map()
        return await cls.get_email_content(email_content_template, all_email_content_map, data)

    @classmethod
    async def get_email_content(cls, email_content_template: EmailContentModel, email_content_map: dict, data: dict, request_type: Optional[str]=None, user_email: Optional[str]=None):
        template_id, template_content = email_content_template.id, email_content_template.content
        if cls.is_content_html(template_content):
            html_content = await CustomJinjaEnvironment.render_text_async(template_content, data)
        else:
            html_content = await cls.get_html_from_content(template_content, email_content_map, data, template_id, request_type, user_email)
        return html_content

    @classmethod
    async def get_html_from_content(cls, jade_content: str, email_content_map: dict, data: dict, template_id: int, request_type: Optional[str]=None, user_email: Optional[str]=None):
        jade_content = cls.expand_email_context(jade_content, email_content_map, [template_id])
        extension = 'jade'
        filename = cls.get_filename(template_id, extension)
        if request_type == 'preview':
            unique_request_id = user_email if user_email else random.randint(1,20)
            prefix_path, directory = cls.get_preview_path()
            filename = '{}-{}'.format(unique_request_id, filename)
        else:    
            prefix_path, directory = cls.get_db_files_path()
        file_path = os.path.join(prefix_path, filename)
        await write_file_async(path=file_path, content=jade_content)
        email_html = await run_in_thread(CustomJinjaEnvironment.render_email, os.path.join(directory, filename), data)
        if request_type == 'preview':
            utils.delete_file(path=file_path)
        return email_html

    @classmethod
    def expand_email_context(cls, content: str, email_content_map: dict, exclude_includes: list = None):
        exclude_includes = exclude_includes or []
        new_formed_text_array = []
        for line in content.splitlines():
            striped_line = line.strip()
            if striped_line.startswith(cls.include_start) and striped_line.endswith(cls.include_end):
                start, end = len(cls.include_start), striped_line.index(cls.include_end)
                unique_identifier = int(striped_line[start:end].strip())
                if unique_identifier not in email_content_map:
                    raise BadRequestException('template id : {} is not exists in email content table'.format(unique_identifier))
                if unique_identifier not in exclude_includes and unique_identifier in email_content_map:
                    number_of_spaces = line.index(cls.include_start)
                    include_content = email_content_map[unique_identifier]
                    expanded_include_content = cls.expand_email_context(include_content, email_content_map,
                                                                        exclude_includes + [unique_identifier])
                    indented_include_content = cls.indent(expanded_include_content, number_of_spaces)
                    new_formed_text_array.append(indented_include_content)
            elif striped_line:
                new_formed_text_array.append(line)
        return '\n'.join(new_formed_text_array)

    @classmethod
    def indent(cls, text, amount, ch=' '):
        return textwrap.indent(text, amount * ch)

    @classmethod
    async def get_all_email_content_map(cls):
        email_contents = await EmailContentRepository.get_all_non_event_email_content()
        return {email_content.id: email_content.content for email_content in email_contents}

    @classmethod
    def is_content_html(cls, content: str):
        content = content or ''
        return '<html' in content

    @classmethod
    def get_filename(cls, template_id, extension: str):
        return '{identifier}.{extension}'.format(identifier=template_id, extension=extension)
    
    @classmethod
    def get_preview_path(cls):
        directory = 'preview'
        return os.path.join(cls.get_templates_path(), 'preview'), directory

    @classmethod
    def get_db_files_path(cls):
        directory = 'db_files'
        return os.path.join(cls.get_templates_path(), directory), directory

    @classmethod
    def get_templates_path(cls):
        return os.path.join(project_root, 'app/utilities/drivers/templates')

    @classmethod
    def check_file_in_cache(cls, path: str, latest_template_version: str):

        if path in cls._existing_files:
            if int(cls._existing_files[path]) >= int(latest_template_version):
                return True
            else:
                cls._existing_files.pop(path, None)
                return False

        file_exists = does_file_exists(path)
        if file_exists:
            cls._existing_files[path] = latest_template_version
        return file_exists

    @classmethod
    async def get_email_details_from_file(cls, template_path: str, data: dict):
        # TODO Can call thread here
        email_body = await run_in_thread(CustomJinjaEnvironment.render_email, template_path, data)
        return email_body

    @classmethod
    def get_all_dependent_events(cls, template_id: str):
        loop_run_count = 0
        max_loop_run_count = 300
        template_events, to_check_template_ids = yield from cls.get_template_events_and_dependencies(template_id)
        while to_check_template_ids and loop_run_count < max_loop_run_count:
            template_id_to_fetch = to_check_template_ids.pop()
            new_events, new_to_check_template_ids = yield from cls.get_template_events_and_dependencies(template_id_to_fetch)
            template_events |= new_events
            to_check_template_ids |= new_to_check_template_ids
            loop_run_count += 1
        return list(template_events)

    @classmethod
    async def get_template_events_and_dependencies(cls, template_id: str):
        template_events, dependencies = set(), set()
        template_include_identifier = cls.get_template_include_identifier(template_id)
        all_includes_data = (await EmailContentRepository.search_emails(content=template_include_identifier, size=200))
        for includes_data in all_includes_data:
            template_id = includes_data.id
            if includes_data.event_id and includes_data.content:
                template_events.add(template_id)
            else:
                dependencies.add(template_id)
        return template_events, dependencies

    @classmethod
    def get_template_include_identifier(cls, template_id):
        return '{}{}{}'.format(cls.include_start, template_id, cls.include_end)    