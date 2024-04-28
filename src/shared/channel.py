from enum import Enum
from loguru import logger
from dataclasses import dataclass
from src.shared.abs_data_class import AbsDataClass, Serializeable

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
        if len(self.name) > 20 or len(self.name) < 3:
            logger.error(f"Name ({self.name}) cannot be more than 20 characters long or less than 3 characters long")
            raise ValueError("Name cannot be more than 20 characters long or less than 3 characters long")
        if self.guild_id <= 0:
            logger.error(f"Guild ID ({self.guild_id}) cannot be less than or equal to 0")
            raise ValueError("Guild ID cannot be less than or equal to 0")