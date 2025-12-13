from enum import Enum


class BaseEnum(Enum):

    @property
    def normalized(self) -> str:
        return self.value.lower().replace(" ", "_")
