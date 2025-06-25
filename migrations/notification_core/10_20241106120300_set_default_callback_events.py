from tortoise import BaseDBAsyncClient

async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
    ALTER TABLE apps
    ALTER COLUMN callback_events
    SET DEFAULT '{}'::jsonb;
    """

async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
    ALTER TABLE apps
    ALTER COLUMN callback_events
    DROP DEFAULT;
    """
