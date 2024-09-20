from sanic import Blueprint
from torpedo import Request, send_response

from app.services.dashboard import DashboardHome


homepage_blueprint = Blueprint("Homepage", url_prefix="dashboard/home")


@homepage_blueprint.route("", methods=["GET"], name="dashboard_home")
async def create_app(request: Request):
    data = await DashboardHome.get_homepage_data()
    return send_response(data)
