from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel # pydanticに標準搭載された


class BaseSchema(BaseModel):
    """全体共通の情報をセットするBaseSchema"""

    model_config = ConfigDict(
      alias_generator=to_camel,
      from_attributes=True,
      populate_by_name=True,
    )


class GetPagination(BaseSchema):
    limit: int = 25
    page: int = 0
    admin: bool = False