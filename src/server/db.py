import random
import string

import gridfs
from loguru import logger
import pymongo
from pymongo import MongoClient
import pymongo.collation
from pymongo.collection import Collection

from src.shared import (AbsDataClass, Attachment, AttachmentType, Channel,
                        ChannelType, Guild, Message, User, attachment)

db_client = MongoClient("mongodb://localhost:27017/")
db = db_client["Lytecord"]
guilds: Collection = db["guilds"]
channels: Collection = db["channels"]
users: Collection = db["users"]
messages: Collection = db["messages"]
passwords: Collection = db["passwords"]
attachments = gridfs.GridFS(db, "attachments")

CASE_INSENSITIVE_COLLATION = pymongo.collation.Collation(locale="en", strength=2)


def convert_id_name(d: dict) -> dict:
    d["id"] = d["_id"]
    del d["_id"]
    return d


def create_indexes():
    messages.create_index("channel_id")
    users.create_index("username", unique=True, collation=CASE_INSENSITIVE_COLLATION)
    channels.create_index("guild_id")
    guilds.create_index("join_code", unique=True)
    logger.warning("Please manually create attachment hash index")


def get_random_hex_code(length=16):
    return ''.join(random.choices(string.hexdigits, k=length))


def get_user_guilds(user_id: int) -> list[Guild]:
    cursor = users.find_one({"_id": user_id})
    if not cursor:
        raise KeyError(f"User with id {user_id} does not exist")

    ids: list[int] = [guild_id for guild_id in cursor["joined_guilds"]]
    return [Guild.from_db_dict(g) for g in guilds.find({"_id": {"$in": ids}}).max_time_ms(1000)]


def does_guild_exist(guild_id: int) -> bool:
    return guilds.find_one({"_id": guild_id}) is not None


def _get_guild_raw(guild_id: int) -> dict:
    result = guilds.find_one({"_id": guild_id})
    if result is None:
        raise KeyError(f"Guild with id {guild_id} does not exist")
    return result


def get_guild(guild_id: int) -> Guild:
    return Guild.from_db_dict(_get_guild_raw(guild_id))


def get_guild_join_code(guild_id: int) -> str:
    return _get_guild_raw(guild_id)["join_code"]


def refresh_guild_join_code(guild_id: int) -> str:
    join_code = get_random_hex_code()

    # Make sure the join code is unique
    while guilds.find_one({"join_code": join_code}) is not None:
        join_code = get_random_hex_code()

    guilds.update_one({"_id": guild_id}, {"$set": {"join_code": join_code}})
    return join_code


def get_guild_by_code(code: str) -> Guild | None:
    guild = guilds.find_one({"join_code": code})
    if guild is None:
        return None
    return Guild.from_db_dict(guild)


def get_guild_owner(guild_id: int) -> int:
    return _get_guild_raw(guild_id)["owner_id"]


def get_channels(guild_id: int) -> list[Channel]:
    return [Channel.from_db_dict(c) for c in channels.find({"guild_id": guild_id}).max_time_ms(1000)]


def _get_channel_raw(channel_id: int) -> dict:
    result = channels.find_one({"_id": channel_id})
    if result is None:
        raise KeyError(f"Channel with id {channel_id} does not exist")
    return result


def get_channel(channel_id: int) -> Channel:
    return Channel.from_db_dict(_get_channel_raw(channel_id))


def does_channel_exist(channel_id: int) -> bool:
    return channels.find_one({"_id": channel_id}) is not None


def _get_user_raw(user_id: int) -> dict:
    result = users.find_one({"_id": user_id})
    if result is None:
        raise KeyError(f"User with id {user_id} does not exist")
    return result


def get_user(user_id: int) -> User:
    return User.from_db_dict(_get_user_raw(user_id))


def get_user_by_name(username: str) -> User:
    result = users.find_one({"username": username}, collation=CASE_INSENSITIVE_COLLATION)
    if result is None:
        raise KeyError(f"User with name {username} does not exist")
    return User.from_db_dict(result)


def does_user_exist(user_id: int) -> bool:
    return users.find_one({"_id": user_id}) is not None


def does_user_exist_by_name(username: str) -> bool:
    return users.find_one({"username": username}, collation=CASE_INSENSITIVE_COLLATION) is not None


def user_join_guild(user_id: int, guild_id: int):
    # Check if the user and guild exist
    if not does_user_exist(user_id):
        raise KeyError(f"User with id {user_id} does not exist")
    if not does_guild_exist(guild_id):
        raise KeyError(f"Guild with id {guild_id} does not exist")

    # Check if the user is already in the guild
    if users.find_one({"_id": user_id, "joined_guilds": guild_id}) is not None:
        return

    guilds.update_one({"_id": guild_id}, {"$push": {"users": user_id}})
    users.update_one({"_id": user_id}, {"$push": {"joined_guilds": guild_id}})


def is_user_in_guild(user_id: int, guild_id: int) -> bool:
    return guilds.find_one({"_id": guild_id, "users": user_id}) is not None


def get_password_hash(user_id: int) -> str:
    result = passwords.find_one({"_id": user_id})
    if result is None:
        raise KeyError(f"Password hash for user with id {user_id} does not exist")
    return result["password_hash"]


def _map_db_message(m: dict):
    """
    Converts a message from the database to a Message object
    by replacing the author_id and attachment_id with the corresponding objects
    """
    author = get_user(m["author_id"])
    m["author"] = author
    del m["author_id"]

    if m["attachment_id"] is not None:
        attachment = get_attachment(m["attachment_id"])
        m["attachment"] = attachment
    else:
        m["attachment"] = None
    del m["attachment_id"]

    return Message.from_db_dict(m)


def get_messages(channel_id: int, from_id: int, count: int) -> list[Message]:
    """
    Returns messages from the given channel before the given id
    """
    if from_id != 0:
        return [_map_db_message(m) for m in
                messages.find({"channel_id": channel_id, "_id": {"$lt": from_id}}).limit(count).sort("_id",-1).max_await_time_ms(1000)]
    return [_map_db_message(m) for m in
            messages.find({"channel_id": channel_id}).limit(count).sort("_id", -1).max_await_time_ms(1000)]


def get_attachment_file(attachment_id: int) -> bytes:
    if not attachments.exists(attachment_id):
        raise KeyError(f"Attachment with id {attachment_id} does not exist")

    return attachments.get(attachment_id).read()


def _get_attachment_raw(attachment_id: int) -> gridfs.GridOut:
    if not attachments.exists(attachment_id):
        raise KeyError(f"Attachment with id {attachment_id} does not exist")

    return attachments.get(attachment_id)


def does_attachment_exist(attachment_id: int) -> bool:
    return attachments.exists(attachment_id)


def get_attachment(attachment_id: int) -> Attachment:
    attachment = _get_attachment_raw(attachment_id)
    filename = attachment.filename
    attachment_type: str = attachment.attachment_type
    width: int = attachment.width
    height: int = attachment.height
    size = attachment.length
    return Attachment(attachment_id, filename, AttachmentType(attachment_type), width, height, size)


def find_attachment_by_hash(hash: str) -> Attachment | None:
    attachment = attachments.find_one({"hash": hash})
    if attachment is None:
        return None
    id = attachment._id
    return get_attachment(id)
