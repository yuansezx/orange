from pydantic import BaseModel, computed_field


class PageResult[DataType](BaseModel):
    page: int
    page_size: int
    total: int
    data: list[DataType] | None = None

    @computed_field
    @property
    def total_pages(self) -> int:
        return (self.total + self.page_size - 1) // self.page_size if self.total else 0
