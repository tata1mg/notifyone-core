from sanic import Blueprint

from .apps import apps_blueprint
from .prepare_notification import notify_bp
from .notification_status import notification_status_blueprint
from .event import event_blueprint, event_with_auth, internal_event_blueprint
from .email import email_api_with_auth, email_blueprint
from .push import push_apis_with_auth
from .sms import sms_apis_with_auth
from .whatsapp import whatsapp_apis_with_auth
from .form.structure import form_bp
from .dashboard.providers import providers_blueprint
from .dashboard.home_page import homepage_blueprint
from .dashboard.settings import settings_blueprint
from .channel_partners  import channel_partners_apis
blueprint_group = Blueprint.group(
    notification_status_blueprint,
    event_blueprint,
    event_with_auth,
    internal_event_blueprint,
    notify_bp,
    email_api_with_auth,
    email_blueprint,
    push_apis_with_auth,
    sms_apis_with_auth,
    whatsapp_apis_with_auth,
    apps_blueprint,
    form_bp,
    providers_blueprint,
    homepage_blueprint,
    settings_blueprint,
    channel_partners_apis
)
