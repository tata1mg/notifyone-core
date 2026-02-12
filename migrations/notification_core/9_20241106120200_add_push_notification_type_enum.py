from tortoise import BaseDBAsyncClient

async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
    DO $$ BEGIN
        CREATE TYPE push_notification_type_enum AS ENUM ('BANNER', 'CALL');
    EXCEPTION
        WHEN duplicate_object THEN null;
    END $$;

    ALTER TABLE push_notification
    ADD COLUMN IF NOT EXISTS type push_notification_type_enum DEFAULT 'BANNER';

    ALTER TYPE push_notification_type_enum ADD VALUE IF NOT EXISTS 'LIVE_ACTIVITY';
    ALTER TYPE push_notification_type_enum ADD VALUE IF NOT EXISTS 'BACKGROUND';
    """

async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
    ALTER TABLE push_notification DROP COLUMN IF EXISTS type;
    -- Dropping enum values not supported in Postgres easily; manual recreation needed
    """
