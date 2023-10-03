from app.routes.api_models.base_api_model import BaseApiModel
from torpedo.constants import HTTPMethod

from sanic_openapi import openapi


class CreateAppInfoEmailOpenApiModel:
    sender_name = openapi.String(description="Sender name to be used in sending email", example="Tata 1mg", required=True)
    sender_address = openapi.String(description="Sender email address to be used in sending email", example="sender@xyzmail.com", required=True)
    reply_to = openapi.String(description="Reply to email address for sending email", example="reply@xyzmail.com", required=True)


class CreateAppInfoOpenApiModel:
    email = CreateAppInfoEmailOpenApiModel


class CreateAppApiModel(BaseApiModel):

    _uri = "/apps"
    _name = "create_app"
    _method: str = HTTPMethod.POST.value
    _summary = "API to create a new app"
    _description = "The API can be used to create new apps in the system"

    class RequestBodyOpenApiModel:
        name = openapi.String(description="App name provided in the request body", example="test_app")
        info = CreateAppInfoOpenApiModel

    class ResponseBodyOpenApiModel:
        id = openapi.Integer(description="ID of the newly created app", example=111)
        name = openapi.String(description="App name provided in the request body", example="test_app")
        message = openapi.String(description="Message string", example="App created successfully")
