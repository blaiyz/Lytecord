from threading import Lock
from datetime import datetime as dt
import random
import string

from src.server import db
from src.shared import Channel, ChannelType, Guild, Message, User, Attachment, AttachmentType
from src.shared.abs_data_class import TAG_LENGTH


lock = Lock()
tag = 0


def _get_random_hex_code(length=16):
    return ''.join(random.choices(string.hexdigits, k=length))

def get_id() -> int:
    global tag
    with lock:
        id = (int(dt.now().timestamp()) << TAG_LENGTH) + tag
        tag = (tag + 1) % (2**TAG_LENGTH)
        return id

def generate_guild(name: str, owner_id: int) -> Guild:
    if db.users.find_one({"_id": owner_id}) is None:
        raise ValueError(f"User with id {owner_id} does not exist")
    
    join_code = _get_random_hex_code()
    while db.guilds.find_one({"join_code": join_code}) is not None:
        join_code = _get_random_hex_code()
    
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

def generate_user(name: str, password_hash: str) -> User:
    u = User(get_id(), name)
    d = u.to_db_dict()
    d["joined_guilds"] = []
    db.users.insert_one(d)
    db.passwords.insert_one({"_id": u.id, "password_hash": password_hash})
    return u

def generate_message(channel_id: int, content: str, attachment_id: int, author: User) -> Message:
    if db.channels.find_one({"_id": channel_id}) is None:
        raise ValueError(f"Channel with id {channel_id} does not exist")
    if db.users.find_one({"_id": author.id}) is None:
        raise ValueError(f"User {author} does not exist")
    # TODO: Check if attachment exists
    
    id = get_id()
    m = Message(id, channel_id, content, attachment_id, author, id >> TAG_LENGTH)
    db.messages.insert_one(m.to_db_dict())
    return m