from lazy_object_proxy.utils import await_
from sanic import Blueprint
from sanic.response import json
from sanic_openapi.openapi2.doc import response
from tortoise_wrapper.exceptions import BadRequestException

from app.constants import NotificationChannels, Providers
from app.services.form.forms import CreateAppForm, CreateEventForm, UpdateAppForm
from app.services.form.forms.add_provider.parent import AddProviderForm

form_bp = Blueprint("form", url_prefix="form-structure/")


@form_bp.get("/create-event")
async def get_create_event_form(_req):
    return json(body=await CreateEventForm.get_asdict_new())


@form_bp.get("/create-app")
async def get_create_app_form(_req):
    return json(body=await CreateAppForm.get_asdict_new())


@form_bp.get("/update-app/<app_id:int>")
async def get_update_app_form(_req, app_id):
    return json(body=await UpdateAppForm.get_instance_asdict(app_id))


@form_bp.get("/add-provider/<channel>/<provider>")
async def get_add_provider_form(_req, channel, provider):
    channel_enum = NotificationChannels.get_enum(channel)
    provider_enum = Providers.get_enum_from_code(provider)
    if not (channel_enum and provider_enum):
        raise BadRequestException("Invalid channel or provider code")
    if provider_enum.value["code"] not in Providers.get_channel_providers(channel_enum):
        raise BadRequestException("Invalid channel provider combination")
    return json(body=await AddProviderForm.get_asdict_with_params(channel=channel_enum, provider=provider_enum))
