from fastapi_camelcase import CamelModel


class GetPagination(CamelModel):
    limit: int = 25
    page: int = 0
    admin: bool = False
    class Config:
        orm_mode = True