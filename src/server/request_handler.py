import functools
import zlib
from loguru import logger
from pymongo.errors import PyMongoError
import base64
from PIL import Image

from src.shared import *
from src.shared import login_utils
from src.server.channel_subscription import ChannelSubscription
from src.server.client import Client
from src.server import channel_manager
from src.server.channel_manager import ServerChannel
from src.server import db
from src.server import asset_generator
from src.shared import attachment


MAX_LOG_SIZE = 2000

def handle_request(req: Request, id: int, subbed: bool, client: Client) -> Request:
    req_type = req.request_type
    
    match req_type:
        case RequestType.AUTHENTICATE if not subbed:
            res_data = authenticate(req.data, client)
        case RequestType.GET_GUILDS if not subbed:
            res_data = get_guilds(req.data, client)
        case RequestType.GET_CHANNELS if not subbed:
            res_data = get_channels(req.data, client)
        case RequestType.GET_MESSAGES if not subbed:
            res_data = get_messages(req.data, client)
        case RequestType.CHANNEL_SUBSCRIPTION if subbed:
            res_data = channel_sub_handler(req.data, client, id)
        case RequestType.CHANNEL_SUBSCRIPTION if not subbed:
            res_data = channel_unsub_handler(req.data, client)
        case RequestType.SEND_MESSAGE if not subbed:
            res_data = handle_new_message(req.data, client)
        case RequestType.CREATE_GUILD if not subbed:
            res_data = handle_create_guild(req.data, client)
        case RequestType.CREATE_CHANNEL if not subbed:
            res_data = handle_create_channel(req.data, client)
        case RequestType.GET_JOIN_CODE if not subbed:
            res_data = handle_get_join_code(req.data, client)
        case RequestType.REFRESH_JOIN_CODE if not subbed:
            res_data = handle_refresh_join_code(req.data, client)
        case RequestType.JOIN_GUILD if not subbed:
            res_data = handle_join_guild(req.data, client)
        case RequestType.GET_ATTACHMENT_FILE if not subbed:
            res_data = handle_attachment_file(req.data, client)
        case RequestType.UPLOAD_ATTACHMENT if not subbed:
            res_data = handle_upload_attachment(req.data, client)
        case _:
            res_data = {"status": "error", "message": "Invalid request type"}
            
    return Request(req_type, res_data)
            
def ensure_correct_data(func):
    @functools.wraps(func)
    def wrapper(data, *args, **kwargs):
        try:
            return func(data, *args, **kwargs)
        except (TypeError, ValueError, KeyError) as e:
            logger.warning(f"Exception: {e} Invalid data: {str(data)[:MAX_LOG_SIZE] if len(str(data)) >= MAX_LOG_SIZE else data} from func: {func.__name__}")
            return {"status": "error", "message": "Invalid data"}
        except PyMongoError as e:
            logger.exception(f"Database error: {e}")
            return {"status": "error", "message": "Database error"}
    return wrapper
            

@ensure_correct_data
def authenticate(data: dict, client: Client) -> dict:
    auth_type: str = data["subtype"]
    username: str = data["username"]
    password: str = data["password"]
    
    if auth_type == "login":
        try:
            user = db.get_user_by_name(username)
        except KeyError:
            # Username not found
            return {"status": "error", "message": "Invalid credentials"}
        
        hash = db.get_password_hash(user.id)
        if login_utils.check_password(password, hash):
            client.user = user
            return {"status": "success", "message": "Authenticated", "user": user}
        
    elif auth_type == "register":
        if not login_utils.is_valid_username(username):
            return {"status": "error", "message": "Invalid username"}
        
        if db.does_user_exist_by_name(username):
            return {"status": "error", "message": "Username already exists"}
        
        if not login_utils.is_valid_password(password):
            return {"status": "error", "message": "Invalid/weak password"}
        
        user = asset_generator.generate_user(username, login_utils.hash_password(password))
        client.user = user
        return {"status": "success", "message": "Registered", "user": user}
        
    return {"status": "error", "message": "Invalid credentials"}


# Temporary function
@ensure_correct_data
def get_guilds(data: dict, client: Client) -> dict:
    if client.user is None:
        return {"status": "error", "message": "Not logged in"}

    guilds = db.get_user_guilds(client.user.id)
    return {"status": "success", "guilds": guilds}

# Temporary function
@ensure_correct_data
def get_channels(data: dict, client: Client) -> dict:
    guild_id: int = data["guild_id"]
    
    channels = db.get_channels(guild_id)
    if len(channels) == 0:
        if db.does_guild_exist(guild_id):
            return {"status": "success", "channels": []}
        return {"status": "error", "message": "Invalid guild id"}
    return {"status": "success", "channels": channels}

# Temporary function
@ensure_correct_data
def get_messages(data: dict, client: Client) -> dict:
    channel_id: int = data["channel_id"]
    before: int = data["before"]
    count: int = data["count"]
    
    logger.debug(f"Getting messages before {before} in channel {channel_id}")
    
    messages = db.get_messages(channel_id, before, count)
    
    if len(messages) == 0:
        if db.does_channel_exist(channel_id):
            return {"status": "success", "messages": []}
        return {"status": "error", "message": "Invalid channel id"}
        
    return {"status": "success", "messages": messages}


@ensure_correct_data
def channel_sub_handler(data: dict, client: Client, subscription_id: int) -> dict:
    subscription = client.current_channel
    subtype: str = data["subtype"]
    
    if subtype == "subscribe":
        if subscription is not None:
            return {"status": "error", "message": "Already subscribed"}
        

        channel_id = data["id"]
        last_message_id = data["last_message_id"]
        try:
            channel: Channel = db.get_channel(channel_id)
        except KeyError:
            return {"status": "error", "message": "Invalid channel id"}
        
        subscription = ChannelSubscription(client, subscription_id, channel)
        client.current_channel = subscription
        subscription.begin(last_message_id)
        
        # For missed messages (if any)
        subscription.wake_up()
        return {"status": "success", "message": f"Subscribed to channel {channel.name} with id: {channel.id}"}
    return {"status": "error", "message": "Invalid subtype (use sub=false to unsubscribe)"}

@ensure_correct_data
def channel_unsub_handler(data: dict, client: Client) -> dict:
    subscription = client.current_channel
    subtype: str = data["subtype"]
    if subtype == "unsubscribe":
        if subscription is None:
            return {"status": "error", "message": "Not subscribed"}
        
        subscription.stop()
        client.current_channel = None
        return {"status": "success", "message": "Unsubscribed"}
    return {"status": "error", "message": "Invalid subtype (use sub=true to subscribe)"}

@ensure_correct_data
def handle_new_message(data: dict, client: Client) -> dict:
    if client.user is None:
        return {"status": "error", "message": "Not logged in"}
    if client.current_channel is None:
        return {"status": "error", "message": "Not subscribed to any channel"}
    
    channel = client.current_channel.channel
    content = data["message"]["content"]
    attachment = Attachment.from_json_serializeable(data["message"]["attachment"])
    
    message = asset_generator.generate_message(channel.id, content, client.user, attachment)
    
    if client.current_channel.send_message(message):
        return {"status": "success", "message": message}
    return {"status": "error", "message": "Failed to send message"}


@ensure_correct_data
def handle_create_guild(data: dict, client: Client) -> dict:
    if client.user is None:
        return {"status": "error", "message": "Not logged in"}
    
    name = data["name"]
    
    try:
        guild = asset_generator.generate_guild(name, client.user.id)
    except ValueError as e:
        return {"status": "error", "message": "Could not create guild"}
    
    return {"status": "success", "guild": guild}

@ensure_correct_data
def handle_create_channel(data: dict, client: Client) -> dict:
    if client.user is None:
        return {"status": "error", "message": "Not logged in"}
    
    name = data["name"]
    guild_id = data["guild_id"]
    
    if not db.does_guild_exist(guild_id):
        return {"status": "error", "message": "Invalid guild id"}
    
    if not client.user.id == db.get_guild_owner(guild_id):
        return {"status": "error", "message": "You are not the owner of this guild"}
    
    try:
        channel = asset_generator.generate_channel(name, ChannelType.TEXT, guild_id)
    except ValueError as e:
        return {"status": "error", "message": "Could not create channel"}
    
    return {"status": "success", "channel": channel}

@ensure_correct_data
def handle_get_join_code(data: dict, client: Client) -> dict:
    if client.user is None:
        return {"status": "error", "message": "Not logged in"}
    
    guild_id = data["guild_id"]
    if not db.does_guild_exist(guild_id):
        return {"status": "error", "message": "Invalid guild id"}
    
    if not client.user.id == db.get_guild_owner(guild_id):
        return {"status": "error", "message": "You are not the owner of this guild"}
    
    return {"status": "success", "code": db.get_guild_join_code(guild_id)}

@ensure_correct_data
def handle_refresh_join_code(data: dict, client: Client) -> dict:
    if client.user is None:
        return {"status": "error", "message": "Not logged in"}
    
    guild_id = data["guild_id"]
    if not db.does_guild_exist(guild_id):
        return {"status": "error", "message": "Invalid guild id"}
    
    if not client.user.id == db.get_guild_owner(guild_id):
        return {"status": "error", "message": "You are not the owner of this guild"}
    
    return {"status": "success", "code": db.refresh_guild_join_code(guild_id)}

@ensure_correct_data
def handle_join_guild(data: dict, client: Client) -> dict:
    if client.user is None:
        return {"status": "error", "message": "Not logged in"}
    
    code = data["code"]
    guild = db.get_guild_by_code(code)
    
    if guild is None:
        return {"status": "error", "message": "Invalid code"}
    
    if db.is_user_in_guild(client.user.id, guild.id):
        return {"status": "error", "message": f"Already in requested guild ({guild.name})"}
    
    db.user_join_guild(client.user.id, guild.id)
    return {"status": "success", "message": "Joined guild", "guild": guild}

@ensure_correct_data
def handle_attachment_file(data: dict, client: Client) -> dict:
    attachment_id = data["attachment_id"]
    if not db.does_attachment_exist(attachment_id):
        return {"status": "error", "message": "Invalid attachment id"}
    
    attachment = db.get_attachment_file(attachment_id)
    
    compressed = zlib.compress(attachment)
    return {"status": "success", "file": base64.b64encode(compressed).decode('ascii')}

@ensure_correct_data
def handle_upload_attachment(data: dict, client: Client) -> dict:
    if client.user is None:
        return {"status": "error", "message": "Not logged in"}
    
    b64: str = data["file"]
    compressed = base64.b64decode(b64)
    file = zlib.decompress(compressed)
    filename: str = data["filename"]
    attachment_type: AttachmentType = AttachmentType.deserialize(data["type"])    

    try:
        attachment = asset_generator.generate_attachment(file, attachment_type, filename)
    except ValueError as e:
        return {"status": "error", "message": f"Could not upload attachment: {e}"}
    
    
    return {"status": "success", "attachment": attachment}