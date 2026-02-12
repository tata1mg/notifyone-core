from tortoise import BaseDBAsyncClient

async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
    ALTER TABLE whatsapp_content
    ADD COLUMN IF NOT EXISTS variable_mapping JSONB DEFAULT '{}'::jsonb;
    """

async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
    ALTER TABLE whatsapp_content DROP COLUMN IF EXISTS variable_mapping;
    """
