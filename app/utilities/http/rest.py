from typing import Any, Dict

from urllib import parse as urlparse

from torpedo.base_http_request import BaseHttpRequest

from app.service_clients.publisher import Publisher, PublishResult, OperatorDetails
from app.constants import NotificationRequestLogStatus


class RestApiClientWrapper(Publisher):
    def __init__(self, host: str, endpoint: str, method: str):
        self._host = host
        self._endpoint = endpoint
        self._method = method

    async def publish(self, payload: Dict[str, Any]) -> PublishResult:
        url = urlparse.urljoin(self._host, self._endpoint)
        response = await BaseHttpRequest.request(
            self._method,
            url,
            data=payload,
            headers={"content-type": "application/json"},
        )
        if response.status == 200:
            publish_result = PublishResult(
                is_success=True,
                status=NotificationRequestLogStatus.SUCCESS,
                message=response.data.get("message"),
                operator_details=OperatorDetails(
                    name=response.data.get("operator", {}).get("name", "UNKNOWN"),
                    event_id=response.data.get("operator", {}).get("event_id", ""),
                ),
            )
        else:
            publish_result = PublishResult(
                is_success=False,
                status=NotificationRequestLogStatus.SUCCESS,
                message=response.data.get("error", {}).get("message")
                or "Something went wrong",
            )
        return publish_result
