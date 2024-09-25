from enum import Enum

from dataclasses import asdict

from sanic_openapi.openapi2.doc import Object


class GenericForm:
    @classmethod
    async def get(cls):
        raise NotImplementedError("method not implemented yet!")

    @classmethod
    async def get_instance(cls, instance_id):
        raise NotImplementedError("method not implemented yet!")

    @classmethod
    async def get_asdict_new(cls):
        def asdict_factory(data):
            def convert_value(obj):
                if isinstance(obj, Enum):
                    return obj.value
                return obj

            return dict((k, convert_value(v)) for k, v in data if v is not None)

        return asdict((await cls.get()), dict_factory=asdict_factory)

    @classmethod
    async def get_asdict_instance(cls, instance_id):
        def asdict_factory(data):
            def convert_value(obj):
                if isinstance(obj, Enum):
                    return obj.value
                return obj

            return dict((k, convert_value(v)) for k, v in data if v is not None)

        return asdict((await cls.get_instance(instance_id)), dict_factory=asdict_factory)
