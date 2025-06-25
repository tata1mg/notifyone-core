import logging
import time

from commonutils.utils import Singleton
from torpedo import CONFIG
from torpedo.exceptions import HTTPRequestTimeoutException
from app.service_clients import LambdaClient

logger = logging.getLogger()


class UrlShortenerCustom(metaclass=Singleton):
    """
    class is used to shorten urls
    """

    def __init__(self):
        self._start_time = int(time.time())

    async def shorten_url(self, url: str):
        _shortened_url = url
        if not self.is_shortening_required(_shortened_url):
            return _shortened_url
        try:
            _shortened_url = await self.lambda_shorten_url(url)
        except HTTPRequestTimeoutException:
            logger.info('Request to shorten url timed out. Client: {}, URL: {}'.format('lambda', url))
        except Exception as e:
            logger.info('Error in shortening URL. Url: {}, Client: {}, Error: {}'.format(url, 'lambda', str(e)))
        return _shortened_url

    @classmethod
    def is_shortening_required(cls, url: str):
        if not url:
            return False
        url_shorten_min_length = CONFIG.config['URL_SHORTENER']['SHORTABLE_URL_MIN_LENGTH'] or 30
        return len(url) >= url_shorten_min_length

    async def lambda_shorten_url(self, long_url: str):
        response = await LambdaClient.shorten_url(long_url)
        return self.extract_payload(response)

    @staticmethod
    def extract_payload(response):
        if response.status == 200:
            return response.data['url']
        else:
            error_msg = response.data.get('message') or 'Unknown error'
            raise Exception(error_msg)
