from app.exceptions import (
    UnAuthorizeException,
    ForbiddenException,
    ResourceNotFoundException
)
from app.service_clients.auth.auth import AuthClient
from torpedo.exceptions import BadRequestException

class HttpRequestAuthentication:
    APP_NAME = "lara"
    LARA_APP = "LARA_APP"
    roles = ["LARA_ADMIN"]

    @classmethod
    async def examine_request(cls, request, *args):
        auth_token = request.headers.get("Authorization", None)
        await cls.validate_authorization(
            auth_token=auth_token, request=request, roles=cls.roles
        )

    @classmethod
    async def validate_authorization(cls, auth_token, request, roles):
        if auth_token is None:
            raise BadRequestException("auth token is required to perform action")
        try:
            user_result = await AuthClient.authenticate(auth_token=auth_token)
        except ResourceNotFoundException:
            raise ForbiddenException(
                "authorization failed: invalid or expired authentication token"
            )
        cls.validate_roles(user_object=user_result, roles=roles)
        request.ctx.user = user_result.get("email")

    @classmethod
    def validate_roles(cls, user_object, roles):
        if user_object is None or not len(
            [app for app in [cls.APP_NAME, cls.LARA_APP] if app in user_object["roles"]]
        ):
            raise UnAuthorizeException("user is not authorized")
        authenticated = False
        for app in [cls.APP_NAME, cls.LARA_APP]:
            for user_role in user_object["roles"].get(app, []):
                if user_role in roles:
                    authenticated = True
        if not authenticated:
            raise ForbiddenException("user is not permitted")
            