from dataclasses import dataclass

from loguru import logger

from src.shared.abs_data_class import AbsDataClass

MAX_NAME_LENGTH = 20
MIN_NAME_LENGTH = 3


@dataclass(frozen=True)
class User(AbsDataClass):
    username: str
    name_color: str

    def __post_init__(self):
        super().__post_init__()
        if len(self.username) > MAX_NAME_LENGTH or len(self.username) < MIN_NAME_LENGTH:
            logger.error(
                f"Name ({self.username}) cannot be more than {MAX_NAME_LENGTH} characters long or less than {MIN_NAME_LENGTH} characters long")
            raise ValueError(
                f"Name cannot be more than {MAX_NAME_LENGTH} characters long or less than {MIN_NAME_LENGTH} characters long")
        if not self.is_valid_hex_color(self.name_color):
            logger.error(f"Name color ({self.name_color}) is not a valid hex color")
            raise ValueError("Name color is not a valid hex color")

    @staticmethod
    def is_valid_hex_color(color: str) -> bool:
        if len(color) != 7 or color[0] != "#":
            return False
        try:
            hex = color[1:]
            int(hex, 16)
            return True
        except ValueError:
            return False

    @staticmethod
    def to_rgb(color: str) -> tuple[int, int, int]:
        return int(color[1:3], 16), int(color[3:5], 16), int(color[5:], 16)

    @staticmethod
    def adjust_brightness(color: str, amount: int) -> str:
        r, g, b = User.to_rgb(color)
        r = min(255, max(0, r + amount))
        g = min(255, max(0, g + amount))
        b = min(255, max(0, b + amount))
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def color_distance(c1: str, c2: str) -> float:
        r1, g1, b1 = User.to_rgb(c1)
        r2, g2, b2 = User.to_rgb(c2)

        return ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5
