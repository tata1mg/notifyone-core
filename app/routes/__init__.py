from sanic import Blueprint

from .apps import apps_blueprint
from .prepare_notification import notify_bp
from .notification_status import notification_status_blueprint
from .event import event_blueprint
from .email import email_blueprint
from .push import push_apis
from .sms import sms_apis
from .whatsapp import whatsapp_apis
from .form.structure import form_bp
from .dashboard.providers import providers_blueprint
from .dashboard.home_page import homepage_blueprint
from .dashboard.settings import settings_blueprint
from .channel_partners  import channel_partners_apis
from app.routes.dashboard.activity_feed import activity_feed_blueprint


blueprint_group = Blueprint.group(
    notification_status_blueprint,
    event_blueprint,
    notify_bp,
    email_blueprint,
    push_apis,
    sms_apis,
    whatsapp_apis,
    apps_blueprint,
    form_bp,
    providers_blueprint,
    homepage_blueprint,
    settings_blueprint,
    channel_partners_apis,
    activity_feed_blueprint
)
