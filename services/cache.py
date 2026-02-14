import time

_cache = {}
TTL_SECONDS = 10


def get_from_cache(key):
    entry = _cache.get(key)
    if not entry:
        return None

    data, timestamp = entry

    if time.time() - timestamp > TTL_SECONDS:
        del _cache[key]
        return None

    return data


def set_cache(key, value):
    _cache[key] = (value, time.time())