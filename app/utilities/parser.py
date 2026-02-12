from typing import Dict
from .response import AsyncTaskResponse

class V2PayloadParser:
    """
    Parses V2 Payload
    V2: {
        "app_name": app_name,
        "event_name": event_name,
        "to": {
            "email": email,
            "mobile": mobile,
        },
        "email": {
            "subject": email_subject,
            "cc": email_cc,
            "bcc": email_bcc,
        },
        "whatsapp": {"body_values": whatsapp_body_values},
        "attachments": attachments,
        "filename": attachments_filename,
        "body": {},
    }
    """

    @classmethod
    def parse(cls, payload: Dict) -> Dict:
        """
        Parse payload for V2 format
        """

        # If payload doesn't `to` field and `email` is string
        # then treat the payload as v1
        if not payload.get("to") and isinstance(payload.get("email"), str):
            return cls._handle_v1_payload(payload)
        # else return as it is
        return payload

    @classmethod
    def _handle_v1_payload(cls, payload: Dict) -> Dict:
        """
        Handle V1 payload and convert to V2 payload

        V1: {
            "app_name": app_name,
            "event_name": event_name,
            "email": email,
            "mobile": mobile,
            "attachments": attachments,
            "filename": attachments_filename,
            "whatsapp": {"body_values": whatsapp_body_values},
            "body": {},
        }
        """

        email = payload.get("email")
        mobile = payload.get("mobile")

        return {
            **payload,
            "to": {"email": email, "mobile": mobile},
            "email": {"subject": None, "cc": None, "bcc": None},
        }

class BaseHttpResponseParser:
    def __init__(self, data, status_code, headers, response_headers_list):
        self._data = data
        self._status_code = status_code
        self._headers = headers
        self._response_headers_list = response_headers_list

    def parse(self) -> AsyncTaskResponse:
        headers = self._prepare_headers()
        return AsyncTaskResponse(
            self._data,
            meta=None,
            status_code=self._status_code,
            headers=headers,
        )

    def _prepare_headers(self):
        final_headers = {}
        if self._headers and self._response_headers_list:
            for key in self._response_headers_list:
                final_headers[key] = self._headers[key]
            return final_headers

        return final_headers


