from sanic import Blueprint
from torpedo import Request, send_response


activity_feed_blueprint = Blueprint("ActivityFeed", url_prefix="dashboard/activity-feed")


@activity_feed_blueprint.route("/search", methods=["GET"], name="search_sent_notification")
async def search_sent_notification(request: Request):
    pass

