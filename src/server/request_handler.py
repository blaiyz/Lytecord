import functools
from loguru import logger

from src.server.channel_subscription import ChannelSubscription
from src.shared import *
from src.server.client import Client
from src.server import channel_manager
from src.server.channel_manager import ServerChannel


TEMPORARY_GUILD_ID = 7189299954974720
TEMPORARY_MESSAGE_ID = 7189649445355520


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
    guilds = [Guild(TEMPORARY_GUILD_ID, "Test Guild")]
    return {"status": "success", "guilds": guilds}

# Temporary function
@ensure_correct_data
def get_channels(data: dict, client: Client) -> dict:
    guild_id: int = data["guild_id"]
    channels = [Channel(TEMPORARY_GUILD_ID + i, f"test channel {i}", ChannelType.TEXT, guild_id) for i in range(1, 6)]
    return {"status": "success", "channels": channels}

# Temporary function
@ensure_correct_data
def get_messages(data: dict, client: Client) -> dict:
    channel_id: int = data["channel_id"]
    before: int = data["before"]
    count: int = data["count"]
    
    logger.debug(f"Getting messages before {before} in channel {channel_id} ;;; type {type(before)}")
    if before != 0:
        return {"status": "success", "messages": []}
    
    messages = [Message(TEMPORARY_MESSAGE_ID + i, channel_id, f"Test message {i}", 0, 1, TEMPORARY_MESSAGE_ID >> 22) for i in range(1, count + 1)]
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
        channel = Channel(channel_id, "Test Channel", ChannelType.TEXT, TEMPORARY_GUILD_ID)
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