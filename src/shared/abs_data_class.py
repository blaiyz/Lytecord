import json
from loguru import logger
from dataclasses import dataclass
from abc import ABC
from typing import Any, Type, TypeVar
from collections import ChainMap

T = TypeVar("T", bound="Serializeable")



class Encoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Serializeable):
            return o.to_dict()
        return super().default(o)
    

# Some type shenanigans, see from_dict method    
def all_annotations(cls) -> ChainMap:
    """Returns a dictionary-like ChainMap that includes annotations for all 
    attributes defined in cls or inherited from superclasses."""
    return ChainMap(*(c.__annotations__ for c in cls.__mro__ if '__annotations__' in c.__dict__) )    

class Serializeable:
    def to_dict(self):
        return {k.strip("_"): v for k, v in self.__dict__.items()}
    
    @classmethod
    def from_dict(cls: Type[T], data: dict[str, Any]) -> T:
        """
        Used for converting a dictionary to an instance of the class,
        after deserializing data to a dictionary.
        """
        try:
            # Get the types of the fields
            field_types = all_annotations(cls)
            logger.debug(f"Field types: {field_types}")
            # Create a new dictionary with the data converted to the correct types
            converted_data = {}
            for field, value in data.items():
                if isinstance(data[field], Serializeable):
                    converted_data[field] = field_types[field](value).from_dict(value)
                else:
                    converted_data[field] = field_types[field](value)
            # Create a new instance of the class with the converted data
            return cls(**converted_data)
        except (KeyError, TypeError):
            raise ValueError(f"Data cannot be converted to {cls.__name__}")
    
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
    


        