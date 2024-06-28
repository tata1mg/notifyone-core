from .response_middleware import add_cors_headers

__all__ = [
    "add_cors_headers"
]

custom_response_middlewares = [
    add_cors_headers
]
