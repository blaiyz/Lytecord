from PIL import Image
from customtkinter import CTkImage
from loguru import logger
from dataclasses import dataclass
from src.shared.abs_data_class import AbsDataClass
# Guild = server
MAX_NAME_LENGTH = 30
MIN_NAME_LENGTH = 3

@dataclass(frozen=True)
class Guild(AbsDataClass):
    name: str
    owner_id: int

    def __post_init__(self):
        super().__post_init__()
        if len(self.name) > MAX_NAME_LENGTH or len(self.name) < MIN_NAME_LENGTH:
            logger.error(f"Name ({self.name}) cannot be more than {MAX_NAME_LENGTH} characters long or less than {MIN_NAME_LENGTH} characters long")
            raise ValueError(f"Name cannot be more than {MAX_NAME_LENGTH} characters long or less than {MIN_NAME_LENGTH} characters long")
        if self.owner_id <= 0:
            logger.error(f"Author ID ({self.owner_id}) cannot be less than or equal to 0")
            raise ValueError("Author ID cannot be less than or equal to 0")

    def get_icon(self)->CTkImage:
        raise NotImplementedError

    