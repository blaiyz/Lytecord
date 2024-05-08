import json
from types import NoneType, UnionType
from loguru import logger
from dataclasses import dataclass
from abc import ABC
import typing
from typing import Any, Optional, Type, TypeVar, Union
from collections import ChainMap

T = TypeVar("T", bound="Serializeable")
TAG_LENGTH = 16


class Encoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Serializeable):
            return o.to_json_serializeable()
        return super().default(o)
    

# Some type shenanigans, see from_json_serializeable method    
def all_annotations(cls) -> ChainMap:
    """
    Returns a dictionary-like ChainMap that includes annotations for all 
    attributes defined in cls or inherited from superclasses
    """
    return ChainMap(*(c.__annotations__ for c in cls.__mro__ if '__annotations__' in c.__dict__) )

def is_optional(field_type):
    """
    Checks if a field type is Optional[...] or Union[..., None]
    """
    return (typing.get_origin(field_type) is UnionType) and (NoneType in typing.get_args(field_type))

class Serializeable:
    def to_json_serializeable(self):
        return {k.strip("_"): v.to_json_serializeable() if isinstance(v, Serializeable) else v for k, v in self.__dict__.items()}
    
    @classmethod
    def from_json_serializeable(cls: Type[T], data: dict[str, Any]) -> T:
        """
        Used for converting a dictionary to an instance of the class,
        after deserializing data to a dictionary.
        """
        try:
            # Get the types of the fields
            field_types = all_annotations(cls)
            field_names = field_types.keys()
            #logger.debug(f"Field types: {field_types}")
            # Create a new dictionary with the data converted to the correct types
            converted_data = {}
            for field, value in data.items():
                if field not in field_names:
                    continue
                field_type = field_types[field]
                if is_optional(field_type):
                    field_type = typing.get_args(field_type)[0]
                    
                #logger.debug(f"Field: {field}, Value: {value}, Type: {field_type}")
                if value is None:
                    converted_data[field] = None
                elif isinstance(value, Serializeable):
                    # Value is already converted, keep it as is
                    converted_data[field] = value
                elif issubclass(field_type, Serializeable):
                    if isinstance(value, dict):
                        # Recursively convert the data
                        converted_data[field] = field_type.from_json_serializeable(value)
                    else:
                        # Reached a primitive type, cannot convert
                        converted_data[field] = field_type(value)
                else:
                    converted_data[field] = field_type(value)
            # Create a new instance of the class with the converted data
            return cls(**converted_data)
        except (KeyError, TypeError) as e:
            logger.exception(f"Cannot convert from data: {e} at class {cls}")
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
        
    def to_db_dict(self):
        """
        Returns a dictionary with the data of the class, with the id renamed to _id.
        Supports nested data classes, as long as they inherit from Serializeable.
        """
        d = {k.strip("_") if k != 'id' else '_id': v.to_json_serializeable() if isinstance(v, Serializeable) else v for k, v in self.__dict__.items()}
        return d

    @classmethod
    def from_db_dict(cls: Type[T], data: dict[str, Any]) -> T:
        #logger.debug(f"From db dict: {data} at class {cls}")
        data["id"] = data.pop("_id")
        return cls.from_json_serializeable(data)

    def __str__(self):
        return json.dumps(self, cls=Encoder, separators=(",",":"))
    