from torpedo import CONFIG
from ..base_api_client import APIClient

class LambdaClient(APIClient):
    """
    auth service client
    """
    _lambda_config = CONFIG.config['LAMBDA']
    _host = _lambda_config['HOST']
    _timeout = 10

    @classmethod
    async def shorten_url(cls, long_url ):
        request_uri = cls._lambda_config['URL_SHORTENER_URI']
        auth = cls._lambda_config['AUTH']
        data = {"auth": auth, "url": long_url}
        response = await cls.post(path=request_uri, data=data, headers={'Content-Type': 'application/json'})
        return response
       