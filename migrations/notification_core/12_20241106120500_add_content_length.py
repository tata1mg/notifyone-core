from tortoise import BaseDBAsyncClient

async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
    ALTER TABLE notification_request_log 
    ADD COLUMN IF NOT EXISTS content_length BIGINT NULL;
    """

async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
    ALTER TABLE notification_request_log 
    DROP COLUMN IF EXISTS content_length;
    """