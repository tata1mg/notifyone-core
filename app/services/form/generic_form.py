from enum import Enum

from dataclasses import asdict


class GenericForm:
    @classmethod
    async def get(cls):
        raise NotImplementedError("method not implemented yet!")

    @classmethod
    async def get_asdict(cls):
        def asdict_factory(data):
            def convert_value(obj):
                if isinstance(obj, Enum):
                    return obj.value
                return obj

            return dict((k, convert_value(v)) for k, v in data if v is not None)

        return asdict((await cls.get()), dict_factory=asdict_factory)
