from sanic import Blueprint
from sanic.response import json

from app.services.form import CreateEventFormData, CreateAppFormData

form_bp = Blueprint("form", url_prefix="form-structure/")


@form_bp.get("/create-event")
async def get_create_event_form(_req):
    return json(body=CreateEventFormData.get())


@form_bp.get("/create-app")
async def get_create_app_form(_req):
    return json(body=CreateAppFormData.get())
