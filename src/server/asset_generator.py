from datetime import datetime as dt
from hashlib import md5
from io import BytesIO
from threading import Lock

from loguru import logger
from PIL import Image

from src.server import db
from src.shared import (Attachment, AttachmentType, Channel, ChannelType,
                        Guild, Message, User, attachment)
from src.shared.abs_data_class import TAG_LENGTH

lock = Lock()
tag = 0


def get_id() -> int:
    global tag
    with lock:
        id = (int(dt.now().timestamp()) << TAG_LENGTH) + tag
        tag = (tag + 1) % (2 ** TAG_LENGTH)
        return id


def generate_guild(name: str, owner_id: int) -> Guild:
    if db.users.find_one({"_id": owner_id}) is None:
        raise ValueError(f"User with id {owner_id} does not exist")

    join_code = db.get_random_hex_code()
    while db.guilds.find_one({"join_code": join_code}) is not None:
        join_code = db.get_random_hex_code()

    g = Guild(get_id(), name, owner_id)
    d = g.to_db_dict()
    d["users"] = []
    d["join_code"] = join_code
    db.guilds.insert_one(d)
    db.user_join_guild(owner_id, g.id)
    return g


def generate_channel(name: str, channel_type: ChannelType, guild_id: int) -> Channel:
    if db.guilds.find_one({"_id": guild_id}) is None:
        raise ValueError(f"Guild with id {guild_id} does not exist")

    c = Channel(get_id(), name, channel_type, guild_id)
    db.channels.insert_one(c.to_db_dict())
    return c


def generate_user(name: str, password_hash: str, name_color: str) -> User:
    u = User(get_id(), name, name_color)
    d = u.to_db_dict()
    d["joined_guilds"] = []
    db.users.insert_one(d)
    db.passwords.insert_one({"_id": u.id, "password_hash": password_hash})
    return u


def generate_message(channel_id: int, content: str, author: User, attachment: Attachment | None) -> Message:
    if db.channels.find_one({"_id": channel_id}) is None:
        raise ValueError(f"Channel with id {channel_id} does not exist")
    if db.users.find_one({"_id": author.id}) is None:
        raise ValueError(f"User {author} does not exist")
    if attachment is not None and db.attachments.find_one({"_id": attachment.id}) is None:
        raise ValueError(f"Attachment {attachment} does not exist")

    id = get_id()
    m = Message(id, channel_id, content, attachment, author, id >> TAG_LENGTH)
    # Convert the author object to author_id to store in the database
    d = m.to_db_dict()
    del d["author"]
    d["author_id"] = author.id

    # Same for attachment
    del d["attachment"]
    if attachment is not None:
        d["attachment_id"] = attachment.id
    else:
        d["attachment_id"] = None

    db.messages.insert_one(d)
    return m


def generate_attachment(data: bytes, attachment_type: AttachmentType, name: str) -> Attachment:
    if len(data) > attachment.MAX_SIZE:
        raise ValueError(f"Attachment data is too large ({len(data)} > {attachment.MAX_SIZE})")

    width, height = 0, 0
    if attachment_type == AttachmentType.IMAGE:
        try:
            image = Image.open(BytesIO(data))
            width, height = image.size
        except Exception as e:
            logger.exception('Failed to analyze image')
            raise ValueError("Failed to analyze image")

    if width > attachment.MAX_WIDTH:
        raise ValueError(f"Width is too large ({width} > {attachment.MAX_WIDTH})")
    elif height > attachment.MAX_HEIGHT:
        raise ValueError(f"Height is too large ({height} > {attachment.MAX_HEIGHT})")

    # Check if the attachment already exists
    hash = md5(data).hexdigest()
    a = db.find_attachment_by_hash(hash)
    if a is not None:
        return a

    id = get_id()
    a = Attachment(id, name, attachment_type, width, height, len(data))
    db.attachments.put(data, _id=id, filename=name, attachment_type=attachment_type.value, width=width, height=height,
                       hash=hash)

    return a
