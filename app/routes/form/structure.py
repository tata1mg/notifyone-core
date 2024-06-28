from sanic import Blueprint
from sanic.response import json

from app.services.form.forms import CreateAppForm, CreateEventForm


form_bp = Blueprint("form", url_prefix="form-structure/")


@form_bp.get("/create-event")
async def get_create_event_form(_req):
    return json(body=await CreateEventForm.get_asdict())


@form_bp.get("/create-app")
async def get_create_app_form(_req):
    return json(body=await CreateAppForm.get_asdict())
