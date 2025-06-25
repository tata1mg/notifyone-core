from typing import Iterable


def _add_cors_headers(response, methods: Iterable[str]) -> None:
    allow_methods = list(set(methods))
    if "OPTIONS" not in allow_methods:
        allow_methods.append("OPTIONS")
    headers = {
        # "Access-Control-Allow-Methods": ",".join(allow_methods),
        "Access-Control-Allow-Methods": "*",
        "Access-Control-Allow-Origin": "*",
        # "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Headers": (
            "origin, content-type, accept, "
            "authorization, x-xsrf-token, x-request-id"
        ),
    }
    response.headers.extend(headers)


async def add_cors_headers(request, response):
    print(f"Request incoming: {request.method} {request.path} {request.route}")
    if request.method == "OPTIONS":
        # For OPTIONS requests, we need to add CORS headers
        # We'll use a default set of methods since there's no route.methods for OPTIONS
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
        _add_cors_headers(response, methods)
    elif hasattr(request, 'route') and request.route is not None:
        # For non-OPTIONS requests with valid routes
        methods = [method for method in request.route.methods]
        _add_cors_headers(response, methods)
    else:
        # For error cases where route might be None
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
        _add_cors_headers(response, methods)