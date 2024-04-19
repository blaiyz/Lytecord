import json
from loguru import logger
from dataclasses import dataclass
from abc import ABC
from typing import Union



@dataclass(frozen=True)
class AbsDataClass(ABC):
    """
    Abstract data class that all data classes inherit from.
    Includes a serialization and deserialization methods.
    All properties are immutable.
    """
    id: int

    def __post_init__(self):
        if 20 < len(str(self.id)):
            logger.error(f"ID ({self.id}) cannot be more than 20 characters long")
            raise ValueError("ID cannot be more than 20 characters long")
        if self.id < 0:
            logger.error(f"ID ({self.id}) cannot be less than 0")
            raise ValueError("ID cannot be less than 0")
        

    def __str__(self):
        return json.dumps(self, default=AbsDataClass.serialize, separators=(",",":"))
    

    @staticmethod
    def serialize(obj: object) -> Union[dict[str, Union[str, int, float, bool, dict, list]], str, int, float, bool, list]:
        if isinstance(obj, AbsDataClass):
            return {k.strip("_"): v for k, v in obj.__dict__.items()}
        return str(obj)

    
    @classmethod
    def deserialize(cls, string: str):
        j = json.loads(string)
        return cls(**j)

        