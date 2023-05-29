from typing import TypeVar, Callable


K = TypeVar('K')
V = TypeVar('V')


def get_or_add_to_dict(d: dict[K, V], key: K, default_factory: Callable[[], V]) -> V:
    if key in d:
        return d[key]
    v = default_factory()
    d[key] = v
    return v
