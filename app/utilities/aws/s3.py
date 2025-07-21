from typing import Dict, Any

from contextlib import AsyncExitStack
import logging

import aiobotocore
import aiobotocore.config

logger = logging.getLogger()


class S3Client:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.session = aiobotocore.session.get_session()
        self.__client = None
        self._s3_client = None

    async def get_s3_client(self):
        if self._s3_client is None:
            self.__client = self.session.create_client(
                "s3",
                region_name=self.config.get("AWS_REGION"),
                endpoint_url=self.config.get("AWS_ENDPOINT_URL"),
                config=aiobotocore.config.AioConfig(
                    max_pool_connections=self.config.get("MAX_POOL_CONNECTIONS", 20),
                ),
            )
            self._s3_client = await self.__client.__aenter__()
        return self._s3_client

    def __del__(self):
        # Close the session when object is getting deleted
        self.__client.__aexit__(None, None, None)

    async def upload(self, bucket: str, content: str, key: str):
        """Upload a file to an S3 bucket"""
        # Upload the file
        try:
            client = await self.get_s3_client()
            response = await client.put_object(Body=content, Bucket=bucket, Key=key)
        except Exception as err:
            logger.error("Error uploading file %s to Bucket %s %s", key, bucket, err)
            return False
        return response
