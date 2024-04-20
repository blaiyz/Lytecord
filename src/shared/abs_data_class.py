import json
from loguru import logger
from dataclasses import dataclass
from abc import ABC
from typing import Union, Callable



class Encoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Serializeable):
            return o.serialize()
        return super().default(o)
    
class Serializeable:
    def serialize(self):
        return {k.strip("_"): v for k, v in self.__dict__.items()}
    
    @staticmethod
    def deserialize(string: str):
        j = json.loads(string)
        return j

@dataclass(frozen=True)
class AbsDataClass(ABC, Serializeable):
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
        return json.dumps(self, cls=Encoder, separators=(",",":"))
    


        