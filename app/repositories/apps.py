from tortoise_wrapper.wrappers import ORMWrapper

from app.caches import NotificationCoreCache
from app.models.notification_core_db import AppsDBModel
from app.models.notification_core import AppsModel

from app.utilities.decorators import redis_cache_decorator_custom


class AppsRepository:

    @staticmethod
    async def _convert_app_to_dict(app_from_db: AppsDBModel) -> dict:
        app = await app_from_db.to_dict()
        app["created"] = app["created"].timestamp()
        app["updated"] = app["updated"].timestamp()
        return app

    @classmethod
    async def get_app_by_name(cls, app_name: str) -> AppsModel:
        app = await cls.get_app_from_db(app_name)
        if app:
            return AppsModel(app)
        return None

    @classmethod
    @redis_cache_decorator_custom(NotificationCoreCache, expire_time=300)
    async def get_app_from_db(cls, app_name: str) -> dict:
        filters = {"name": app_name}
        apps_from_db = await ORMWrapper.get_by_filters(AppsDBModel, filters, limit=1)
        if apps_from_db:
            return await cls._convert_app_to_dict(apps_from_db[0])
        return dict()

    @classmethod
    async def create_app(cls, name, info):
        values = {
            "name": name,
            "info": info
        }
        row = await ORMWrapper.create(AppsDBModel, values)
        return AppsModel(await cls._convert_app_to_dict(row))
