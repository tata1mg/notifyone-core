from lazy_object_proxy.utils import await_
from sanic import Blueprint
from sanic.response import json
from sanic_openapi.openapi2.doc import response

from app.services.form.forms import CreateAppForm, CreateEventForm, UpdateAppForm


form_bp = Blueprint("form", url_prefix="form-structure/")


@form_bp.get("/create-event")
async def get_create_event_form(_req):
    return json(body=await CreateEventForm.get_asdict_new())


@form_bp.get("/create-app")
async def get_create_app_form(_req):
    return json(body=await CreateAppForm.get_asdict_new())


@form_bp.get("/update-app/<app_id:int>")
async def get_update_app_form(_req, app_id):
    return json(body=await UpdateAppForm.get_asdict_instance(app_id))
