from dataclasses import dataclass

from loguru import logger

from src.shared.abs_data_class import TAG_LENGTH, AbsDataClass
from src.shared.attachment import Attachment
from src.shared.user import User

MAX_MESSAGE_LENGTH = 1500
TAG_BYTE_LENGTH = TAG_LENGTH


@dataclass(frozen=True)
class Message(AbsDataClass):
    # ID is an integer where the first 16 bits are a tag and the rest is a timestamp
    # This allows to sort messages by id and have multiple messages with the same timestamp
    # (This is similar to Discord's snowflake system)
    channel_id: int
    content: str
    # attachment_id is 0 if there is no attachment
    attachment: Attachment | None
    author: User
    timestamp: int

    def __post_init__(self):
        super().__post_init__()
        if len(self.content) > MAX_MESSAGE_LENGTH:
            logger.error(f"Content ({self.content}) cannot be more than {MAX_MESSAGE_LENGTH} characters long")
            raise ValueError(f"Content cannot be more than {MAX_MESSAGE_LENGTH} characters long")
        if self.channel_id <= 0:
            logger.error(f"Channel ID ({self.channel_id}) cannot be less than or equal to 0")
            raise ValueError("Channel ID cannot be less than or equal to 0")
        if self.timestamp <= 0:
            logger.error(f"Timestamp ({self.timestamp}) cannot be less than or equal to 0")
            raise ValueError("Timestamp cannot be less than or equal to 0")
        if self.timestamp != self.id >> TAG_BYTE_LENGTH:
            logger.error(
                f"Timestamp ({self.timestamp}) must be equal to the upper bits of ID ({self.id}) (the first {TAG_BYTE_LENGTH} bits are the tag)")
            raise ValueError(
                f"Timestamp must be equal to the upper bits of ID (the first {TAG_BYTE_LENGTH} bits are the tag)")

    def sort_key(self):
        return -self.id
