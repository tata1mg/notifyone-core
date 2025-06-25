from torpedo import CONFIG
from torpedo.parser import BaseApiResponseParser
from ..base_api_client import APIClient


class AuthClient(APIClient):
    """
    auth service client
    """
    auth_config = CONFIG.config['AUTH']
    _host = auth_config['HOST']
    _timeout = auth_config['TIMEOUT']
    _parser = BaseApiResponseParser

    @classmethod
    async def get_devices_by_email_id(cls, email_id: str):
        path = '/v6/devices'
        payload = {
            'email': email_id
        }
        devices = await cls.post(path, data=payload)
        return devices.data
    
    @classmethod
    async def authenticate(cls, auth_token):
        """
        This is used for authenticating given auth by calling identity service.
        :param auth_token: auth token which will be authenticated.
        :return: dict of response from identity service.
        """
        path = '/v6/authenticate'
        payload = {
            'authentication_token': auth_token
        }
        response = await cls.post(path, data=payload)
        return response.data