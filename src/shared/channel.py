import re
from dataclasses import dataclass
from enum import Enum

from loguru import logger

from src.shared.abs_data_class import AbsDataClass, Serializeable

MAX_NAME_LENGTH = 20
MIN_NAME_LENGTH = 3
REGEX = re.compile(r"^[a-z0-9\-]{3,20}$")


class ChannelType(Serializeable, Enum):
    TEXT = "text"
    VIDEO = "video"

    def to_json_serializeable(self):
        return self.name.lower()

    @classmethod
    def from_json_serializeable(cls, data: dict[str, str]):
        return ChannelType[data["type"].upper()]

    @classmethod
    def deserialize(cls, string: str):
        return cls[string.upper()]


@dataclass(frozen=True)
class Channel(AbsDataClass):
    name: str
    type: ChannelType
    guild_id: int

    def __post_init__(self):
        super().__post_init__()

        if not self.name.islower():
            logger.error(f"Name ({self.name}) must be all lowercase")
            raise ValueError("Name must be all lowercase")
        if len(self.name) > MAX_NAME_LENGTH or len(self.name) < MIN_NAME_LENGTH:
            logger.error(f"Name ({self.name}) cannot be more than 20 characters long or less than 3 characters long")
            raise ValueError("Name cannot be more than 20 characters long or less than 3 characters long")
        if not REGEX.match(self.name):
            logger.error(f"Name ({self.name}) must only contain lowercase letters, numbers, and hyphens")
            raise ValueError("Name must only contain lowercase letters, numbers, and hyphens")
        if self.guild_id < 0:
            logger.error(f"Guild ID ({self.guild_id}) cannot be less than 0")
            raise ValueError("Guild ID cannot be less than 0")
