from loguru import logger
from dataclasses import dataclass
from src.shared.abs_data_class import AbsDataClass

MAX_MESSAGE_LENGTH = 1500


@dataclass(frozen=True)
class Message(AbsDataClass):
    channel_id: int
    content: str
    # attachment_id is 0 if there is no attachment
    attachment_id: int
    author_id: int
    timestamp: int

    def __post_init__(self):
        super().__post_init__()
        if len(self.content) > MAX_MESSAGE_LENGTH:
            logger.error(f"Content ({self.content}) cannot be more than {MAX_MESSAGE_LENGTH} characters long")
            raise ValueError(f"Content cannot be more than {MAX_MESSAGE_LENGTH} characters long")
        if self.channel_id <= 0:
            logger.error(f"Channel ID ({self.channel_id}) cannot be less than or equal to 0")
            raise ValueError("Channel ID cannot be less than or equal to 0")
        if self.attachment_id < 0:
            logger.error(f"Attachment ID ({self.attachment_id}) cannot beless than 0")
            raise ValueError("Attachment ID cannot be less than 0")
        if self.author_id <= 0:
            logger.error(f"Author ID ({self.author_id}) cannot be less than or equal to 0")
            raise ValueError("Author ID cannot be less than or equal to 0")
        if self.timestamp <= 0:
            logger.error(f"Timestamp ({self.timestamp}) cannot be less than or equal to 0")
            raise ValueError("Timestamp cannot be less than or equal to 0")
        
    
    def sort_key(self):
        return -self.timestamp