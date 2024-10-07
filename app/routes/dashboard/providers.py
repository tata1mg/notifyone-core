from sanic import Blueprint
from torpedo import Request, send_response

from app.services.dashboard import DashboardProvidersScreen


providers_blueprint = Blueprint("Providers", url_prefix="dashboard/providers")


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
