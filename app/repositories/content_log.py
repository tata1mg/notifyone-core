from typing import Any, Dict, Optional

from app.constants.notification_channels import NotificationChannels
from app.utilities.aws.s3 import S3Client


class ContentLogRepository:
    BUCKET_NAME = ""
    S3_CLIENT = None
    CHANNEL_EXT = {
        NotificationChannels.EMAIL: "html",
        NotificationChannels.SMS: "txt",
        NotificationChannels.PUSH: "json",
        NotificationChannels.WHATSAPP: "txt",
    }

    @classmethod
    def init(cls, config: Dict[str, Any]) -> None:
        cls.config = config
        cls.S3_CLIENT = S3Client(config)
        cls.BUCKET_NAME = config.get("BUCKET_NAME", "NSContentLogs")

    @classmethod
    async def create(
        cls,
        request_id: str,
        channel: NotificationChannels,
        content: str,
        message: Optional[str] = None,
    ):
        ext = cls.CHANNEL_EXT.get(channel, "txt")
        key = f"{request_id}/{channel}.{ext}"

        if not content:
            content = message
        await cls.S3_CLIENT.upload(bucket=cls.BUCKET_NAME, content=content, key=key)
