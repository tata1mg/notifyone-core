from crypt import methods

from sanic import Blueprint
from torpedo import Request, send_response
from tortoise_wrapper.exceptions import BadRequestException

from app.constants import NotificationChannels, Providers
from app.services.dashboard import DashboardProvidersScreen


providers_blueprint = Blueprint("Providers", url_prefix="dashboard/providers")


@providers_blueprint.route("", methods=["POST"], name="add_new_provider")
async def add_new_provider(request: Request):
    data = request.custom_json()
    resp = await DashboardProvidersScreen.add_new_provider(data)
    return send_response(resp)


@providers_blueprint.route("", methods=["PUT"], name="update_provider")
async def update_provider(request: Request):
    data = request.custom_json()
    resp = await DashboardProvidersScreen.update_provider(data)
    return send_response(resp)


@providers_blueprint.route("/list", methods=["GET"], name="dashboard_providers")
async def list_channels_and_respective_providers(request: Request):
    data = await DashboardProvidersScreen.get_channels_and_providers()
    return send_response(data)


@providers_blueprint.route("/configured", methods=["GET"], name="dashboard_providers_configured")
async def list_channels_and_respective_providers(request: Request):
    request_params = request.request_params()
    limit = request_params.get("limit") or 10
    offset = request_params.get("offset") or 0
    data = await DashboardProvidersScreen.get_configured_providers(limit, offset)
    return send_response(data)

