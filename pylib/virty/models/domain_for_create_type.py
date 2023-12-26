from enum import Enum


class DomainForCreateType(str, Enum):
    MANUAL = "manual"
    PROJECT = "project"

    def __str__(self) -> str:
        return str(self.value)
