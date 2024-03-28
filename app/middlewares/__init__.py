from .response_middleware import add_mandatory_response_headers

__all__ = [
    "add_mandatory_response_headers"
]

custom_response_middlewares = [
    add_mandatory_response_headers
]
