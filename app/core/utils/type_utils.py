from collections.abc import Hashable


def to_set(value: Hashable | list | set) -> set:
    if isinstance(value, set):
        return value
    if isinstance(value, list):
        return set(value)
    return {value}
