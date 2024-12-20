from torpedo import Request, send_response
from sanic import Blueprint
from torpedo.exceptions import BadRequestException

from app.constants import NotificationChannels
from app.services.channel_partners import ChannelPartners

channel_partners_apis = Blueprint("ChannelPartnersAPIs", url_prefix="channel_partners")


@channel_partners_apis.route("/configurations", methods=["GET"], name="get_channel_partners_configurations")
async def get_channel_partners_configurations(request: Request):
    request_params = request.request_params()
    channels = request_params.get("channels") or None
    if not channels:
        raise BadRequestException("Channels missing in request param")
    channels = channels.split(",")
    channels = [str(attr).strip() for attr in channels]
    channels_enum = list()
    for channel in channels:
        channel_enum = NotificationChannels.get_enum(channel)
        if not channel_enum:
            raise BadRequestException(f"Invalid channel - {channel}")
        channels_enum.append(channel_enum)
    resp = await ChannelPartners.get_channel_partners_config_for_channels(channels_enum)
    return send_response(resp)