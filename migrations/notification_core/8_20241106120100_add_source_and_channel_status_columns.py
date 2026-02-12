from tortoise import BaseDBAsyncClient

async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
    ALTER TABLE notification_request_log
    ADD COLUMN IF NOT EXISTS source notification_request_log_source_enum DEFAULT 'UNKNOWN';

    ALTER TABLE notification_request_attempt
    ADD COLUMN IF NOT EXISTS source notification_request_log_source_enum DEFAULT 'UNKNOWN';

    ALTER TABLE notification_request_log
    ADD COLUMN IF NOT EXISTS channel_status TEXT DEFAULT 'UNKNOWN';

    ALTER TABLE notification_request_attempt
    ADD COLUMN IF NOT EXISTS channel_status TEXT DEFAULT 'UNKNOWN';
    """

async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
    ALTER TABLE notification_request_log DROP COLUMN IF EXISTS source;
    ALTER TABLE notification_request_attempt DROP COLUMN IF EXISTS source;
    ALTER TABLE notification_request_log DROP COLUMN IF EXISTS channel_status;
    ALTER TABLE notification_request_attempt DROP COLUMN IF EXISTS channel_status;
    """
