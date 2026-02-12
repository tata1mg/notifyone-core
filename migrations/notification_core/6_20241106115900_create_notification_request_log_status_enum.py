from tortoise import BaseDBAsyncClient

async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
    DO $$ BEGIN
        CREATE TYPE notification_request_log_status_enum AS ENUM (
            'NEW', 'INITIATED', 'FAILED', 'SUCCESS'
        );
    EXCEPTION
        WHEN duplicate_object THEN null;
    END $$;
    """

async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
    DROP TYPE IF EXISTS notification_request_log_status_enum;
    """
