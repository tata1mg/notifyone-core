from tortoise import BaseDBAsyncClient

async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
    DO $$ BEGIN
        CREATE TYPE notification_request_log_source_enum AS ENUM ('INTERNAL', 'WEBHOOK', 'UNKNOWN');
    EXCEPTION
        WHEN duplicate_object THEN null;
    END $$;

    ALTER TYPE notification_request_log_status_enum ADD VALUE IF NOT EXISTS 'QUEUED';
    ALTER TYPE notification_request_log_status_enum ADD VALUE IF NOT EXISTS 'PENDING';
    """

async def downgrade(db: BaseDBAsyncClient) -> str:
    return """""
    -- PostgreSQL does not support removing individual enum values easily
    -- Downgrade would need to recreate the enum, which is typically skipped
    """