"""新規passwordの共通検証。既存hashの照合規則とは分離する。"""

import re
from typing import Annotated

from pydantic import AfterValidator, Field
from pydantic_core import PydanticCustomError


def validate_new_password(value: str) -> str:
    if (
        len(value) < 8
        or len(value.encode("utf-8")) > 72
        or re.search(r"\s", value)
        or "\x00" in value
        or not all(re.search(pattern, value) for pattern in (
            r"[a-z]", r"[A-Z]", r"\d", r"[^A-Za-z0-9]",
        ))
    ):
        raise PydanticCustomError("password_policy", "The password does not meet the policy.")
    return value


NewPassword = Annotated[
    str,
    Field(min_length=8, max_length=72, json_schema_extra={"writeOnly": True}),
    AfterValidator(validate_new_password),
]
