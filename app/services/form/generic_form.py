from enum import Enum

from dataclasses import asdict


class GenericForm:
    @classmethod
    async def get(cls):
        raise NotImplementedError("method not implemented yet!")

    @classmethod
    async def get_with_params(cls, **kwargs):
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
    async def get_asdict_with_params(cls, **kwargs):
        def asdict_factory(data):
            def convert_value(obj):
                if isinstance(obj, Enum):
                    return obj.value
                return obj

            return dict((k, convert_value(v)) for k, v in data if v is not None)

        return asdict((await cls.get_with_params(**kwargs)), dict_factory=asdict_factory)

    @classmethod
    async def get_instance_asdict(cls, instance_id):
        def asdict_factory(data):
            def convert_value(obj):
                if isinstance(obj, Enum):
                    return obj.value
                return obj

            return dict((k, convert_value(v)) for k, v in data if v is not None)

        return asdict((await cls.get_instance(instance_id)), dict_factory=asdict_factory)
