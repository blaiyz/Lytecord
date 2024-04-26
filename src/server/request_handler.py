import functools
from loguru import logger
import bisect
from datetime import datetime as dt

from src.server.channel_subscription import ChannelSubscription
from src.shared import *
from src.server.client import Client
from src.server import channel_manager
from src.server.channel_manager import ServerChannel


TEMPORARY_GUILD_ID = 7189299954974720
TEMPORARY_MESSAGE_ID = 7189649445355520


TEST_DB = {
    "guilds": [ 
            {
            "guild": Guild(TEMPORARY_GUILD_ID, "Test Guild"),
            "channels": [ {
                    "channel": Channel(TEMPORARY_GUILD_ID + i, f"test channel {i}", ChannelType.TEXT, TEMPORARY_GUILD_ID),
                    "messages": [
                        Message(TEMPORARY_MESSAGE_ID + i, TEMPORARY_GUILD_ID + i, f"Test message {i}", 0, 1, TEMPORARY_MESSAGE_ID >> 22)
                        for i in range(300, 0, -1)
                    ]
                }
                for i in range(1, 6)
            ]
        }
    ]
}


def handle_request(req: Request, id: int, subbed: bool, client: Client) -> Request:
    req_type = req.request_type
    
    match req_type:
        case RequestType.AUTHENTICATION if not subbed:
            res_data = authenticate(req.data)
        case RequestType.GET_GUILDS if not subbed:
            res_data = get_guilds(req.data, client)
        case RequestType.GET_CHANNELS if not subbed:
            res_data = get_channels(req.data, client)
        case RequestType.GET_MESSAGES if not subbed:
            res_data = get_messages(req.data, client)
        case RequestType.CHANNEL_SUBSCRIPTION if subbed:
            res_data = channel_sub_handler(req.data, client, id)
        case RequestType.SEND_MESSAGE if not subbed:
            res_data = handle_new_message(req.data, client)
        case _:
            res_data = {"status": "error", "message": "Invalid request type"}
            
    return Request(req_type, res_data)
            
def ensure_correct_data(func):
    @functools.wraps(func)
    def wrapper(data, *args, **kwargs):
        try:
            return func(data, *args, **kwargs)
        except (TypeError, ValueError, KeyError):
            logger.debug(f"Invalid data: {data} from func: {func.__name__}")
            return {"status": "error", "message": "Invalid data"}
    return wrapper
            

@ensure_correct_data
def authenticate(data: dict) -> dict:
    username: str = data["username"]
    password: str = data["password"]
    
    # Temporary
    if username == "" and password == "":
        return {"status": "success", "message": "Authenticated"}
    return {"status": "error", "message": "Invalid credentials"}


# Temporary function
@ensure_correct_data
def get_guilds(data: dict, client: Client) -> dict:
    # Check later for user
    guilds = [guild_db["guild"] for guild_db in TEST_DB["guilds"]]
    return {"status": "success", "guilds": guilds}

# Temporary function
@ensure_correct_data
def get_channels(data: dict, client: Client) -> dict:
    guild_id: int = data["guild_id"]
    
    if guild_id != TEMPORARY_GUILD_ID:
        return {"status": "error", "message": "Invalid guild id"}
    
    channel_db = TEST_DB["guilds"][0]["channels"]
    
    channels = [c["channel"] for c in channel_db]
    return {"status": "success", "channels": channels}

# Temporary function
@ensure_correct_data
def get_messages(data: dict, client: Client) -> dict:
    channel_id: int = data["channel_id"]
    before: int = data["before"]
    count: int = data["count"]
    
    logger.debug(f"Getting messages before {before} in channel {channel_id}")
    
    all_messages: list[Message] = [c for c in TEST_DB["guilds"][0]["channels"] if c["channel"].id == channel_id][0]["messages"]
    
    if before == 0:
        messages = all_messages[:count]
    else:
        if all_messages[-1].id >= before:
            messages = []
        else:
            index = bisect.bisect_right(all_messages, -before, key=lambda x: x.sort_key())
            logger.debug(f"Index: {index}, i+c: {min(index + count, len(all_messages))}")
            messages = all_messages[index:min(index + count, len(all_messages))]
        
    return {"status": "success", "messages": messages}


@ensure_correct_data
def channel_sub_handler(data: dict, client: Client, subscription_id: int) -> dict:
    subscription = client.current_channel
    subtype: str = data["subtype"]
    
    if subtype == "subscribe":
        if subscription is not None:
            return {"status": "error", "message": "Already subscribed"}

        # Change to actually check if channel exists
        channel_id = data["id"]
        channel: Channel = [c for c in TEST_DB["guilds"][0]["channels"] if c["channel"].id == channel_id][0]["channel"]
        subscription = ChannelSubscription(client, subscription_id, channel)
        client.current_channel = subscription
        subscription.begin()
        return {"status": "success", "message": f"Subscribed to channel {channel.name} with id: {channel.id}"}
    
    elif subtype == "unsubscribe":
        if subscription is None:
            return {"status": "error", "message": "Not subscribed"}
        
        subscription.stop()
        client.current_channel = None
        return {"status": "success", "message": "Unsubscribed"}
    return {"status": "error", "message": "Invalid subtype"}


@ensure_correct_data
def handle_new_message(data: dict, client: Client) -> dict:
    if client.current_channel is None:
        return {"status": "error", "message": "Not subscribed to any channel"}
    
    channel = client.current_channel.channel
    content = data["message"]["content"]
    t = int(dt.now().timestamp())
    message = Message(t << 22, channel.id, content, 0, 1, t)
    if client.current_channel.send_message(message):
        return {"status": "success", "message": message}
    return {"status": "error", "message": "Failed to send message"}