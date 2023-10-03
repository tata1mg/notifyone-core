from redis_wrapper.client import RedisCache
from torpedo import CONFIG
from app.constants.email import Email

config = CONFIG.config

class NotificationCoreCache(RedisCache):
    _service_prefix = CONFIG.config["NAME"]
    _key_prefix = "global"
    _expire_in_sec = 1 * 60 * 60  # 1 hour default cache

    @classmethod
    async def set_key(cls, key, value, expire=None):
        return await cls.set(key, value, expire=expire)

    @classmethod
    async def get_key(cls, key):
        return await cls.get(key)


class CacheKey:
    args_separator = "_"
    namespace_key_separator = ":"

    @classmethod
    def get_keys(cls):
        return {
            "TEMPLATES_SEARCH_CACHE": {
                "name": "TEMPLATES_SEARCH_CACHE",
                "expiry": cls.get_email_crud_expiry(),
            },
            "TEMPLATE_GET_PREVIEWS": {
                "name": "TEMPLATE_GET_PREVIEWS",
                "expiry": cls.get_email_crud_expiry(),
            },
        }

    @classmethod
    def get_email_crud_expiry(cls):
        return (
            config.get("EMAIL_CRUD_CAHCE_EXPIRY_IN_SECONDS")
            or Email.REDIS_EXPIRY_TIME_LONG
        )

    @classmethod
    def make_key(cls, key: str, *args, namespace: str = None):
        args = (args and list(args)) or []
        args = [str(argument) for argument in args]
        args.sort()
        key = (
            "{}{}{}".format(namespace, cls.namespace_key_separator, key)
            if namespace
            else key
        )
        key_parts = [key] + args
        return cls.args_separator.join(key_parts)

    @classmethod
    def get_preview_cache_key(cls, user_id, template_id):
        return cls.make_key(
            CacheKey.get_keys()["TEMPLATE_GET_PREVIEWS"]["name"], user_id, template_id
        )

class CacheHelper:
    CACHE_KEYS_DATA = CacheKey.get_keys()

    @classmethod
    async def handle_template_update(cls, template_id, updated_by):
        await NotificationCoreCache.delete_by_prefix(
            cls.CACHE_KEYS_DATA["TEMPLATES_SEARCH_CACHE"]["name"]
        )
        await cls.delete_preview_cache(updated_by, template_id)

    @classmethod
    async def create_preview_cache(
        cls, user_id: str, template_id, template_ids_affected: list
    ):
        key = CacheKey.get_preview_cache_key(user_id, template_id)
        return await NotificationCoreCache.set(
            key,
            template_ids_affected,
            int(CacheKey.get_keys()["TEMPLATE_GET_PREVIEWS"]["expiry"]),
        )

    @classmethod
    async def get_preview_cache(cls, user_id: str, template_id):
        key = CacheKey.get_preview_cache_key(user_id, template_id)
        return await NotificationCoreCache.get(key)

    @classmethod
    async def delete_preview_cache(cls, user_id: str, template_id):
        key = CacheKey.get_preview_cache_key(user_id, template_id)
        return await NotificationCoreCache.delete(key)
