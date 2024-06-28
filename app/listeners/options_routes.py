from collections import defaultdict
from typing import Dict, FrozenSet

from sanic import response as sanic_response
from sanic.router import Route
from sanic_routing.exceptions import RouteExists

from app.middlewares.response_middleware import _add_cors_headers


async def setup_options(app, loop):
    app.router.reset()
    needs_options = _compile_routes_needing_options(app.router.routes_all)
    for uri, methods in needs_options.items():
        try:
            app.add_route(
                _options_wrapper(options_handler, methods),
                uri,
                methods=["OPTIONS"],
            )
        except RouteExists as re:
            pass
    app.router.finalize()


def _compile_routes_needing_options(
    routes: Dict[str, Route]
) -> Dict[str, FrozenSet]:
    needs_options = defaultdict(list)
    # This is 21.12 and later. You will need to change this for older versions.
    for route in routes.values():
        if "OPTIONS" not in route.methods and "swagger" not in route.path:
            needs_options[route.uri].extend(route.methods)

    return {
        uri: frozenset(methods) for uri, methods in dict(needs_options).items()
    }


def _options_wrapper(handler, methods):
    def wrapped_handler(request, *args, **kwargs):
        nonlocal methods
        return handler(request, methods)

    return wrapped_handler


async def options_handler(request, methods) -> sanic_response.HTTPResponse:
    resp = sanic_response.empty(status=200)
    _add_cors_headers(resp, methods)
    return resp
