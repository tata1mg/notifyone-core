from sanic import Blueprint
from .prepare_notification import notify_bp
from .notification_status import notification_status_blueprint
from .event import event_blueprint
from app.routes.channel_partners import channel_partners_apis
from app.routes.email import email_apis
from app.routes.push import push_apis
from app.routes.sms import sms_apis
from app.routes.whatsapp import whatsapp_apis
from app.routes.apps import apps_blueprint
from app.routes.form.structure import form_bp
from app.routes.dashboard.home_page import homepage_blueprint
from app.routes.dashboard.providers import providers_blueprint
from app.routes.dashboard.settings import settings_blueprint
from app.routes.dashboard.activity_feed import activity_feed_blueprint


blueprint_group = Blueprint.group(
    notification_status_blueprint,
    event_blueprint,
    notify_bp,
    email_apis,
    push_apis,
    sms_apis,
    whatsapp_apis,
    apps_blueprint,
    form_bp,
    homepage_blueprint,
    providers_blueprint,
    settings_blueprint,
    activity_feed_blueprint,
    channel_partners_apis
)
