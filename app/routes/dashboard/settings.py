from sanic import Blueprint
from torpedo import Request, send_response
from app.services.dashboard import DashboardSettingsScreen


settings_blueprint = Blueprint("Settings", url_prefix="dashboard/settings")


@settings_blueprint.route("/default-priority", methods=["POST"], name="add_default_provider_priority")
async def add_default_provider_priority(request: Request):
    data = request.custom_json()
    resp = await DashboardSettingsScreen.upsert_default_provider_priority_for_channel(data)
    return send_response(resp)

@settings_blueprint.route("/default-priority/all", methods=["GET"], name="get_default_provider_priority")
async def get_default_provider_priority(request: Request):
    resp = await DashboardSettingsScreen.get_default_priority_all()
    return send_response(resp)


@settings_blueprint.route("/dynamic-priority", methods=["POST"], name="add_dynamic_provider_priority")
async def add_dynamic_provider_priority(request: Request):
    data = request.custom_json()
    resp = await DashboardSettingsScreen.upsert_dynamic_provider_priority_for_channel(data)
    return send_response(resp)

@settings_blueprint.route("/dynamic-priority/all", methods=["GET"], name="get_dynamic_provider_priority")
async def get_dynamic_provider_priority(request: Request):
    resp = await DashboardSettingsScreen.get_dynamic_priority_all()
    return send_response(resp)
