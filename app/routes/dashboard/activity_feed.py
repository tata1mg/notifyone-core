from sanic import Blueprint
from torpedo import Request, send_response

from app.services.dashboard.activity_feed import DashboardActivityFeedScreen

activity_feed_blueprint = Blueprint("ActivityFeed", url_prefix="dashboard/activity-feed")


@activity_feed_blueprint.route("/search", methods=["GET"], name="search_sent_notification")
async def search_sent_notification(request: Request):
    request_params = request.request_params()
    resp = await DashboardActivityFeedScreen.search_sent_notifications(request_params)
    return send_response(resp)
