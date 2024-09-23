from sanic import Blueprint
from torpedo import Request, send_response

from app.services.dashboard import DashboardHomeScreen


homepage_blueprint = Blueprint("Homepage", url_prefix="dashboard/home")


@homepage_blueprint.route("", methods=["GET"], name="dashboard_home")
async def get_homepage_data(request: Request):
    data = await DashboardHomeScreen.get_homepage_data()
    return send_response(data)
