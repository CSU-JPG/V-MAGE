from typing import Dict


def kget(obj, *keys, default=None):

    if obj is None:
        return default

    for key in keys:
        try:
            obj = obj[key]
        except (KeyError, IndexError):
            return default

    return obj


def get_with_warning(obj: Dict, key, default=None):
    if obj is None:
        return default

    try:
        obj = obj[key]
    except (KeyError, IndexError):
        return default

    return obj