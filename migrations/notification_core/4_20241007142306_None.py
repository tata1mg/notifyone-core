from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "providers" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "unique_identifier" VARCHAR(200) NOT NULL UNIQUE,
    "provider" TEXT NOT NULL,
    "channel" VARCHAR(8) NOT NULL,
    "status" VARCHAR(8) NOT NULL  DEFAULT 'active',
    "configuration" JSONB NOT NULL,
    "created" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "providers"."channel" IS 'EMAIL: email\nSMS: sms\nWHATSAPP: whatsapp\nPUSH: push';
COMMENT ON COLUMN "providers"."status" IS 'ACTIVE: active\nDISABLED: disabled';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "providers";"""
