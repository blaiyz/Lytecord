from loguru import logger
from pymongo import MongoClient

from src.shared import AbsDataClass, Channel, ChannelType, Guild, Message, User, Attachment, AttachmentType


db_client = MongoClient("mongodb://localhost:27017/")
db = db_client["Lytecord"]
guilds = db["guilds"]
channels = db["channels"]
users = db["users"]
messages = db["messages"]
attachments = db["attachments"]


# TODO: get the guilds from the user collection
def get_guilds() -> list[Guild]:
    return [Guild.from_db_dict(g) for g in guilds.find()]

def does_guild_exist(guild_id: int) -> bool:
    return guilds.find_one({"_id": guild_id}) is not None

def get_channels(guild_id: int)-> list[Channel]:
    return [Channel.from_db_dict(c) for c in channels.find({"guild_id": guild_id}).max_time_ms(1000)]

def get_channel(channel_id: int) -> Channel:
    result = channels.find_one({"_id": channel_id})
    if result is None:
        raise ValueError(f"Channel with id {channel_id} does not exist")
    return Channel.from_db_dict(result)

def does_channel_exist(channel_id: int) -> bool:
    return channels.find_one({"_id": channel_id}) is not None

def does_user_exist(user_id: int) -> bool:
    return users.find_one({"_id": user_id}) is not None

def get_messages(channel_id: int, from_id: int, count: int) -> list[Message]:
    """
    Returns messages from the given channel before the given id
    """
    if from_id != 0:
        return [Message.from_db_dict(m) for m in messages.find({"channel_id": channel_id, "_id": {"$lt": from_id}}).limit(count).sort("_id", -1)]
    return [Message.from_db_dict(m) for m in messages.find({"channel_id": channel_id}).limit(count).sort("_id", -1)]



