import base64
from enum import Enum
from turtle import width
from loguru import logger
from dataclasses import dataclass
from src.shared.abs_data_class import AbsDataClass, Serializeable
from io import BytesIO
from PIL import Image

MAX_SIZE = 2**24
MAX_WIDTH = 2**12
MAX_HEIGHT = 2**12


class AttachmentType(Serializeable, Enum):
    IMAGE = "image"
    OTHER = "other"

    def __str__(self):
        return self.name.lower()
    
    def to_json_serializeable(self):
        return self.name.lower()
    
    @classmethod
    def deserialize(cls, string: str):
        return cls[string.upper()]
    

@dataclass(frozen=True)
class Attachment(AbsDataClass):
    filename: str
    a_type: AttachmentType
    width: int
    height: int
    size: int

    def __post_init__(self):
        super().__post_init__()
        if len(self.filename) > 30 or len(self.filename) < 3:
            logger.error(f"Name ({self.filename}) cannot be more than 30 characters long or less than 3 characters long")
            raise ValueError("Name cannot be more than 30 characters long or less than 3 characters long")
        
        if self.size <= 0:
            logger.error(f"Attachment size ({self.size}) cannot be less than or equal to 0")
            raise ValueError("Attachment size cannot be less than or equal to 0")
        if self.size > MAX_SIZE:
            logger.error(f"Attachment size ({self.size}) cannot be more than {MAX_SIZE}")
            raise ValueError(f"Attachment size cannot be more than {MAX_SIZE}")
        
        if self.a_type == AttachmentType.IMAGE:
            if self.width <= 0:
                logger.error(f"Width ({self.width}) cannot be less than or equal to 0")
                raise ValueError("Width cannot be less than or equal to 0")
            if self.width > MAX_WIDTH:
                logger.error(f"Width ({self.width}) cannot be more than {MAX_WIDTH}")
                raise ValueError(f"Width cannot be more than {MAX_WIDTH}")
            if self.height <= 0:
                logger.error(f"Height ({self.height}) cannot be less than or equal to 0")
                raise ValueError("Height cannot be less than or equal to 0")
            if self.height > MAX_HEIGHT:
                logger.error(f"Height ({self.height}) cannot be more than {MAX_HEIGHT}")
                raise ValueError(f"Height cannot be more than {MAX_HEIGHT}")
        else:
            if self.width != 0:
                logger.error(f"Width ({self.width}) must be 0")
                raise ValueError("Width must be 0")
            if self.height != 0:
                logger.error(f"Height ({self.height}) must be 0")
                raise ValueError("Height must be 0")

    def __str__(self, with_blob: bool = True):
        if with_blob:
            return super().__str__()
        return f"Attachment(id: {self.id}, name: {self.filename}, type: {self.a_type}, {self.width}, {self.height})"