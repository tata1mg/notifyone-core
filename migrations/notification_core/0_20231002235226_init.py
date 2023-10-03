from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "apps" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(100) NOT NULL UNIQUE,
    "info" JSONB NOT NULL,
    "created" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "email_content" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "event_id" BIGINT NOT NULL UNIQUE,
    "subject" TEXT NOT NULL,
    "content" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    "name" VARCHAR(100) NOT NULL UNIQUE,
    "path" VARCHAR(500) NOT NULL,
    "updated_by" VARCHAR(100) NOT NULL,
    "created" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "event" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "event_name" VARCHAR(100) NOT NULL,
    "app_name" VARCHAR(100) NOT NULL,
    "actions" JSONB NOT NULL,
    "created" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "subject" VARCHAR(100) NOT NULL,
    "updated_by" VARCHAR(100) NOT NULL,
    "event_type" VARCHAR(100) NOT NULL,
    "triggers_limit" JSONB NOT NULL,
    "meta_info" JSONB NOT NULL,
    "is_deleted" BOOL NOT NULL,
    CONSTRAINT "uid_event_event_n_f9cdbe" UNIQUE ("event_name", "app_name")
);
CREATE TABLE IF NOT EXISTS "generic_data_store" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "category" VARCHAR(100) NOT NULL,
    "identifier" VARCHAR(1000) NOT NULL,
    "event_id" BIGINT NOT NULL,
    "data" JSONB NOT NULL,
    "created" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_by" VARCHAR(100) NOT NULL,
    CONSTRAINT "uid_generic_dat_identif_a44fce" UNIQUE ("identifier", "category")
);
CREATE TABLE IF NOT EXISTS "notification_request_attempt" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "log_id" BIGINT NOT NULL,
    "channel" VARCHAR(100) NOT NULL,
    "sent_to" VARCHAR(5000),
    "status" VARCHAR(50) NOT NULL  DEFAULT 'NEW',
    "operator" VARCHAR(50),
    "operator_event_id" VARCHAR(200),
    "message" VARCHAR(5000),
    "metadata" VARCHAR(5000),
    "attempt_number" INT NOT NULL,
    "sent_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "idx_notificatio_operato_2fddec" ON "notification_request_attempt" ("operator_event_id");
CREATE INDEX IF NOT EXISTS "idx_notificatio_created_054fa8" ON "notification_request_attempt" ("created");
CREATE TABLE IF NOT EXISTS "notification_request_log" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "event_id" BIGINT NOT NULL,
    "notification_request_id" VARCHAR(100) NOT NULL,
    "channel" VARCHAR(100) NOT NULL,
    "sent_to" VARCHAR(1000),
    "source_identifier" VARCHAR(1000),
    "status" VARCHAR(12) NOT NULL  DEFAULT 'NEW',
    "operator" VARCHAR(50),
    "operator_event_id" VARCHAR(200),
    "message" TEXT,
    "metadata" TEXT,
    "created" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "idx_notificatio_notific_6679d2" ON "notification_request_log" ("notification_request_id");
CREATE INDEX IF NOT EXISTS "idx_notificatio_sent_to_516858" ON "notification_request_log" ("sent_to");
CREATE INDEX IF NOT EXISTS "idx_notificatio_source__201dff" ON "notification_request_log" ("source_identifier");
CREATE INDEX IF NOT EXISTS "idx_notificatio_operato_530a49" ON "notification_request_log" ("operator_event_id");
CREATE INDEX IF NOT EXISTS "idx_notificatio_created_0551e3" ON "notification_request_log" ("created");
CREATE INDEX IF NOT EXISTS "idx_notificatio_source__7eada4" ON "notification_request_log" ("source_identifier", "event_id");
COMMENT ON COLUMN "notification_request_log"."status" IS 'NEW: NEW\nINITIATED: INITIATED\nFAILED: FAILED\nSUCCESS: SUCCESS\nUSER_OPT_OUT: USER_OPT_OUT\nNOT_ELIGIBLE: NOT_ELIGIBLE';
CREATE TABLE IF NOT EXISTS "push_notification" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "event_id" BIGINT NOT NULL UNIQUE,
    "title" VARCHAR(1000) NOT NULL,
    "body" VARCHAR(1000) NOT NULL,
    "target" VARCHAR(1000) NOT NULL,
    "image" VARCHAR(1000) NOT NULL,
    "device_type" VARCHAR(50) NOT NULL,
    "device_version" VARCHAR(50) NOT NULL,
    "updated_by" VARCHAR(100) NOT NULL,
    "created" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "sms_content" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "event_id" BIGINT NOT NULL UNIQUE,
    "content" TEXT NOT NULL,
    "updated_by" VARCHAR(100) NOT NULL,
    "created" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "whatsapp_content" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "event_id" BIGINT NOT NULL UNIQUE,
    "name" TEXT NOT NULL,
    "updated_by" VARCHAR(100) NOT NULL,
    "created" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
