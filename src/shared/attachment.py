import base64
from enum import Enum
from turtle import width
from loguru import logger
from dataclasses import dataclass
from src.shared.abs_data_class import AbsDataClass
from io import BytesIO
from PIL import Image

MAX_SIZE = 2**24
MAX_WIDTH = 2**12
MAX_HEIGHT = 2**12


class AttachmentType(Enum):
    IMAGE = 0
    OTHER = 1

    def __str__(self):
        return self.name.lower()
    

@dataclass(frozen=True)
class Attachment(AbsDataClass):
    filename: str
    type: AttachmentType
    width: int
    height: int
    # Base64 encoded
    blob: str

    def __post_init__(self):
        super().__post_init__()
        if len(self.filename) > 30 or len(self.filename) < 3:
            logger.error(f"Name ({self.filename}) cannot be more than 30 characters long or less than 3 characters long")
            raise ValueError("Name cannot be more than 30 characters long or less than 3 characters long")
        
        size = Attachment.calculate_size(self.blob)
        if size <= 0:
            logger.error(f"Attachment size ({size}) cannot be less than or equal to 0")
            raise ValueError("Attachment size cannot be less than or equal to 0")
        if size > MAX_SIZE:
            logger.error(f"Attachment size ({size}) cannot be more than {MAX_SIZE}")
            raise ValueError(f"Attachment size cannot be more than {MAX_SIZE}")
        
        if AttachmentType == AttachmentType.IMAGE:
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
        return f"Attachment(id: {self.id}, name: {self.filename}, type: {self.type}, {self.width}, {self.height})"
    
    def get_image(self):
        if self.type != AttachmentType.IMAGE:
            return None
        return Image.open(BytesIO(base64.b64decode(self.blob, validate=True)))
    
    @staticmethod
    def calculate_size(blob: str) -> int:
        return int((len(blob) * 3) / 4 - blob.count('=', -2))
    
    @staticmethod
    def from_image(image: Image.Image, filename: str) -> "Attachment":
        blob = base64.b64encode(image.tobytes()).decode()
        width, height = image.size
        return Attachment(0, filename, AttachmentType.IMAGE, width, height, blob)