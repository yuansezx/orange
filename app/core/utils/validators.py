from typing import TypeVar

IdType = TypeVar('IdType')

def check_unique(
    id_to_check: IdType | None,
    exclude_id: IdType | None = None,
) -> bool:
    if id_to_check is None:
        return True
    if exclude_id is not None and id_to_check == exclude_id:
        return True
    return False

