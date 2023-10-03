import re
import datetime
from jinja2 import PackageLoader, Environment
from premailer import Premailer
import logging

logger = logging.getLogger()

name_slug_pattern = re.compile(r'[^A-Za-z0-9.]')
name_slug_replace_string = '-'
name_slug_replace_multiple = re.compile(r'-+')
name_slug_replace_leading_trailing = re.compile(r'^-|-*$')


def format_eta_timestamp(timestamp: int):
    if timestamp and (isinstance(timestamp, int) or isinstance(timestamp, float)):
        return datetime.datetime.fromtimestamp(int(timestamp)).strftime('%-d %b, %Y')


def convert_epoch_to_ist_date(timestamp: int):
    actual_time = int(timestamp) + (5.5 * 60 * 60)
    return datetime.datetime.fromtimestamp(actual_time).strftime("%d-%b")


def format_eta_timestamp_with_hour(timestamp: int):
    if timestamp and (isinstance(timestamp, int) or isinstance(timestamp, float)):
        return datetime.datetime.fromtimestamp(int(timestamp)).strftime('%-d %b, %Y %-I %p')


def get_total_neucoins(payment_summary: dict):
    """
    This is used to calculate total Neucoins used in payment_summary for
    CAD's Jinja templates.
    """
    if not (payment_summary and isinstance(payment_summary, dict)):
        return 0.0
    neucoins_v1 = 0.0
    online_payment_tenders = payment_summary.get('online_payment_tenders') or {}
    if online_payment_tenders and online_payment_tenders.get('TATA_POINT'):
        tata_point = online_payment_tenders.get('TATA_POINT')
        if tata_point.get('amount', 0) > 0:
            neucoins_v1 += int(tata_point.get('amount'))
    return round(neucoins_v1, 2)


def strip_status(status):
    if not status:
        return ""
    else:
        if status.find("Rx Rejected") != -1:
            return "Invalid prescription"
        return status


def get_slug_from_name(name):
    if not name:
        return None
    else:
        replaced_string = re.sub(name_slug_replace_leading_trailing, '',
                                 re.sub(name_slug_replace_multiple, name_slug_replace_string,
                                        re.sub(name_slug_pattern, name_slug_replace_string, name)))
        return replaced_string.lower()


class CustomJinjaEnvironment:

    jinja_environment = None
    default_render_response = ''

    @classmethod
    async def set_jinja_env(cls):
        cls.jinja_environment = cls.get_jinja_environment()

    @staticmethod
    def get_jinja_environment() -> Environment:
        """
        Function is used to get a Jinja environment with additional customizations required
        :return: Environment object
        """
        # Create Jinja environment with pyjade extension
        env = Environment(loader=PackageLoader('app.utilities.drivers', 'templates'),extensions=['pyjade.ext.jinja.PyJadeExtension'])
        # Add filters required in rendering mails and sms
        env.filters['get_slug_from_name'] = get_slug_from_name
        env.filters['strip_status'] = strip_status
        env.filters['format_eta_timestamp'] = format_eta_timestamp
        env.filters['format_eta_timestamp_with_hour'] = format_eta_timestamp_with_hour
        env.filters['convert_epoch_to_ist_date'] = convert_epoch_to_ist_date
        env.filters['get_total_neucoins'] = get_total_neucoins
        return env

    @classmethod
    def render_text(cls, text: str, data: dict):
        if not (text and data):
            return cls.default_render_response
        return cls._templatise_and_render(text, data)

    @classmethod
    async def render_text_async(cls, text: str, data: dict):
        if not text:
            return cls.default_render_response
        from app.utilities import run_in_thread
        result = await run_in_thread(cls._templatise_and_render, text, data)
        return result

    @classmethod
    def _templatise_and_render(cls, text: str, data: dict):
        template = cls.jinja_environment.from_string(text)
        return template.render(data)

    @classmethod
    def render_html(cls, html_path: str, data: dict):
        if not (html_path and data):
            return cls.default_render_response
        template = cls.jinja_environment.get_template(html_path)
        return template.render(data)

    @classmethod
    def render_email(cls, html_path: str, data: dict):
        html_rendered_text = cls.render_html(html_path, data)
        if not html_rendered_text:
            return cls.default_render_response
        _premailer = Premailer(html_rendered_text, cssutils_logging_handler=logger, cssutils_logging_level=logging.FATAL)
        return _premailer.transform()
