from crypt import methods
from os.path import defpath

from attr import dataclass
from sanic import Blueprint
from sanic_openapi import openapi

from torpedo import Request, send_response

from app.services.apps import AppService
from app.routes.api_models.apps import CreateAppApiModel
from app.utilities.drivers.jinja.jinja_environment import name_slug_pattern

apps_blueprint = Blueprint("Apps")


@apps_blueprint.route(CreateAppApiModel.uri(), methods=[CreateAppApiModel.http_method()], name=CreateAppApiModel.name())
@openapi.definition(
    summary=CreateAppApiModel.summary(),
    description=CreateAppApiModel.description(),
    body={
        CreateAppApiModel.request_content_type(): CreateAppApiModel.RequestBodyOpenApiModel
    },
    response={
        CreateAppApiModel.response_content_type(): CreateAppApiModel.ResponseBodyOpenApiModel
    }
)
async def create_app(request: Request):
    request_payload = request.custom_json()
    data = await AppService.create_app(request_payload)
    return send_response(data)


@apps_blueprint.route("/apps", methods=["GET"], name="get_apps")
async def get_apps(request: Request):
    data = await AppService.get_all_apps()
    return send_response(data)


@apps_blueprint.route("/apps", methods=["PUT"], name="update_app")
async def update_app(request: Request):
    request_payload = request.custom_json()
    data = await AppService.update_app(request_payload)
    return send_response(data)
