from dataclasses import dataclass

from customtkinter import CTkImage
from loguru import logger
from PIL import Image

from src.shared.abs_data_class import AbsDataClass

MAX_NAME_LENGTH = 20
MIN_NAME_LENGTH = 3

@dataclass(frozen=True)
class User(AbsDataClass):
    username: str

    def __post_init__(self):
        super().__post_init__()
        if len(self.username) > MAX_NAME_LENGTH or len(self.username) < MIN_NAME_LENGTH:
            logger.error(f"Name ({self.username}) cannot be more than {MAX_NAME_LENGTH} characters long or less than {MIN_NAME_LENGTH} characters long")
            raise ValueError(f"Name cannot be more than {MAX_NAME_LENGTH} characters long or less than {MIN_NAME_LENGTH} characters long")

    def get_icon(self)->CTkImage:
        raise NotImplementedError

    