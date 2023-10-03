import asyncio
import hashlib
import inspect
import json
from functools import wraps


def redis_cache_decorator_custom(redis_manager_class, expire_time=0, timeouts: dict=None):
    def wrapped(func):
        @wraps(func)
        async def apply_cache(*args, **kwargs):
            _args = ''
            if args and len(args) > 0:
                _args = str(args[1:])
            cls_name = inspect.getmodule(func).__name__ if inspect.getmodule(func) else ''
            redis_key = json.dumps({'func': func.__name__, 'args': _args, 'kwargs': kwargs, 'func_cls': cls_name}, sort_keys=True)
            digest_key = hashlib.md5(redis_key.encode('utf-8')).hexdigest()

            get_timeout = timeouts['get'] if timeouts and 'get' in timeouts else 5
            set_timeout = timeouts['set'] if timeouts and 'set' in timeouts else 5

            try:
                result = await asyncio.wait_for(redis_manager_class.get_key(digest_key), timeout=get_timeout)
            except asyncio.TimeoutError:
                result = None
            except Exception as e:
                result = None

            if result is not None:
                return json.loads(result)

            result = await func(*args, **kwargs)

            if not result :
                return result
            try:
                await asyncio.wait_for(redis_manager_class.set_key(digest_key, json.dumps(result), expire=expire_time), timeout=set_timeout)
            except Exception as e:
                pass
            return result
        return apply_cache
    return wrapped
