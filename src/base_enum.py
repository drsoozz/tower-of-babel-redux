from enum import Enum
from typing import Self


class BaseEnum(Enum):

    @property
    def normalized(self) -> str:
        self.value: str
        normalized = self.value.lower().translate(str.maketrans({" ": "_", "-": "_"}))
        return normalized

    @classmethod
    def enum_from_string(cls, value: str) -> Self:
        try:
            return cls(value)
        except ValueError as exc:
            raise ValueError(f"Invalid {cls.__name__}: {value!r}") from exc
