from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "providers_default_priority" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "channel" VARCHAR(8) NOT NULL UNIQUE,
    "priority" JSONB NOT NULL,
    "status" VARCHAR(8) NOT NULL  DEFAULT 'active',
    "created" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "providers_default_priority"."channel" IS 'EMAIL: email\nSMS: sms\nWHATSAPP: whatsapp\nPUSH: push';
COMMENT ON COLUMN "providers_default_priority"."status" IS 'ACTIVE: active\nDISABLED: disabled';
        CREATE TABLE IF NOT EXISTS "providers_dynamic_priority" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "channel" VARCHAR(8) NOT NULL UNIQUE,
    "priority_logic" TEXT NOT NULL,
    "status" VARCHAR(8) NOT NULL  DEFAULT 'active',
    "created" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "providers_dynamic_priority"."channel" IS 'EMAIL: email\nSMS: sms\nWHATSAPP: whatsapp\nPUSH: push';
COMMENT ON COLUMN "providers_dynamic_priority"."status" IS 'ACTIVE: active\nDISABLED: disabled';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "providers_default_priority";
        DROP TABLE IF EXISTS "providers_dynamic_priority";"""
