from customtkinter import CTk

from dataclasses import dataclass
import ssl
import socket
from typing import Callable
from loguru import logger
from functools import wraps
from enum import Enum
import base64

from src.shared.attachment import Attachment
from src.shared.protocol import HOST
from src.shared import Request, RequestType, Channel, ChannelType, Guild, Message, login_utils
from src.client.request_manager import RequestManager
from src.shared.user import User



def ensure_correct_data(default: tuple, callback: Callable):
    def outer(func: Callable[[Request], None]):
        @wraps(func)
        def inner(req: Request):
            try:
                func(req)
            except (TypeError, ValueError, KeyError) as e:
                logger.exception(f"Exception: {e} Invalid data: {req.data} from func: {callback.__name__}")
                callback(*default)
        return inner
    return outer

@dataclass
class Subscription:
    channel: Channel | None
    id: int | None
    last_message_id: int = 0
    
    
class AuthType(Enum):
    LOGIN = "login"
    REGISTER = "register"
    
    def opp(self):
        """
        Returns the oppsite of the current mode.
        If current mode is LOGIN, returns SIGNUP and vice versa.
        """
        if self == AuthType.LOGIN:
            return AuthType.REGISTER
        return AuthType.LOGIN

class Client():
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        # Deal with certificate verification later
        self.context = ssl._create_unverified_context()
        self.sock = self.context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname=self.ip)

        self.user: User | None = None
        self.subscription = Subscription(None, None)
        
    def begin(self, app: CTk):
        self.sock.connect((self.ip, self.port))
        self.sock.setblocking(True)
        self.request_manager = RequestManager(self.sock, app)
        self.request_manager.begin()
        
        
    def authenticate(self, subtype: AuthType, username: str, password: str, callback: Callable[[bool, str], None]):
        @ensure_correct_data(default=(False,), callback=callback)
        def c(req: Request):
            msg = req.data["message"]
            status = req.data["status"] == "success"
            if status and msg == "Authenticated" or msg == "Registered":
                self.user = User.from_json_serializeable(req.data["user"])
                logger.info(f"logged in with user: {self.user}")
                callback(True, 'Authenticated')
            callback(False, msg)
        
        
        request = Request(RequestType.AUTHENTICATE, {"username": username, "password": password, "subtype": subtype.value})
        self.request_manager.request(request, callback=c)
        
    def get_guilds(self, callback: Callable[[list[Guild]], None]):
        @ensure_correct_data(default=([],), callback=callback)
        def c(req: Request):
            if req.data["status"] == "success":
                guilds = [Guild.from_json_serializeable(guild) for guild in req.data["guilds"]]
                callback(guilds)
            else:
                callback([])
        
        request = Request(RequestType.GET_GUILDS, {})
        self.request_manager.request(request, callback=c)
        
    def get_channels(self, guild_id: int, callback: Callable[[list[Channel]], None]):
        @ensure_correct_data(default=([],), callback=callback)
        def c(req: Request):
            if req.data["status"] == "success":
                channels = [Channel.from_json_serializeable(channel) for channel in req.data["channels"]]
                callback(channels)
            else:
                callback([])
        
        request = Request(RequestType.GET_CHANNELS, {"guild_id": guild_id})
        self.request_manager.request(request, callback=c)
        
    def get_messages(self, channel_id: int, from_id: int, count: int, callback: Callable[[list[Message]], None]):
        @ensure_correct_data(default=([],), callback=callback)
        def c(req: Request):
            if req.data["status"] == "success":
                messages = [Message.from_json_serializeable(message) for message in req.data["messages"]]
                if len(messages) > 0:
                    self.subscription.last_message_id = messages[0].id
                callback(messages)
            else:
                callback([])
        
        request = Request(RequestType.GET_MESSAGES, {"channel_id": channel_id, "before": from_id, "count": count})
        self.request_manager.request(request, callback=c)
        
    def subscribe_channel(self, channel: Channel, callback: Callable[[Message | None], None]):
        if self.subscription.id is not None:
            logger.warning("Already subscribed (or subscribing) to a channel, please unsubscribe first")
            return
        
        c_id = channel.id
        confirmation = {"status": False}
        @ensure_correct_data(default=(None,), callback=callback)
        def c(req: Request):
            if confirmation["status"]:
                message = Message.from_json_serializeable(req.data["message"])
                callback(message)
                return
            
            if req.data["status"] == "success":
                confirmation["status"] = True
                self.subscription.channel = channel
            else:
                self.subscription.id = None
        
        request = Request(RequestType.CHANNEL_SUBSCRIPTION, {"subtype": "subscribe", "id": c_id, "last_message_id": self.subscription.last_message_id})
        self.subscription.id = self.request_manager.subscribe(request, callback=c)
        
    def unsubscribe_channel(self):
        if self.subscription.channel is None or self.subscription.id is None:
            logger.warning("Not subscribed to any channel")
            return
        
        id = self.subscription.id
        self.subscription.channel = None
        self.subscription.id = None
        self.subscription.last_message_id = 0
        self.request_manager.unsubscribe(id, Request(RequestType.CHANNEL_SUBSCRIPTION, {"subtype": "unsubscribe"}))
        
    def send_message(self, message: Message, callback: Callable[[Message | None], None]):
        if self.subscription.channel is None:
            logger.warning("Not subscribed to any channel")
            return
        
        @ensure_correct_data(default=(None,), callback=callback)
        def c(req: Request):
            if req.data["status"] == "success":
                message = Message.from_json_serializeable(req.data["message"])
                callback(message)
            else:
                callback(None)
        
        request = Request(RequestType.SEND_MESSAGE, {"message": message})
        self.request_manager.request(request, callback=c)
        
    def create_guild(self, name: str, callback: Callable[[Guild | None, str], None]):
        @ensure_correct_data(default=(None, 'Unexpected client error'), callback=callback)
        def c(req: Request):
            if req.data["status"] == "success":
                guild = Guild.from_json_serializeable(req.data["guild"])
                callback(guild, '')
            else:
                message: str = req.data["message"]
                callback(None, message)
        
        request = Request(RequestType.CREATE_GUILD, {"name": name})
        self.request_manager.request(request, callback=c)
        
    def create_channel(self, name: str, guild_id: int, callback: Callable[[Channel | None, str], None]):   
        @ensure_correct_data(default=(None, 'Unexpected client error'), callback=callback)
        def c(req: Request):
            if req.data["status"] == "success":
                channel = Channel.from_json_serializeable(req.data["channel"])
                callback(channel, '')
            else:
                message: str = req.data["message"]
                callback(None, message)
        
        request = Request(RequestType.CREATE_CHANNEL, {"name": name, "guild_id": guild_id, "type": ChannelType.TEXT})
        self.request_manager.request(request, callback=c)
    
    def get_guild_join_code(self, guild_id: int, callback: Callable[[str | None], None]):
        @ensure_correct_data(default=(None,), callback=callback)
        def c(req: Request):
            if req.data["status"] == "success":
                callback(req.data["code"])
            else:
                callback(None)
        
        request = Request(RequestType.GET_JOIN_CODE, {"guild_id": guild_id})
        self.request_manager.request(request, callback=c)
        
    def refresh_guild_join_code(self, guild_id: int, callback: Callable[[str | None], None]):
        @ensure_correct_data(default=(None,), callback=callback)
        def c(req: Request):
            if req.data["status"] == "success":
                callback(req.data["code"])
            else:
                callback(None)
        
        request = Request(RequestType.REFRESH_JOIN_CODE, {"guild_id": guild_id})
        self.request_manager.request(request, callback=c)
    
            
    def join_guild(self, code: str, callback: Callable[[Guild | None, str], None]):
        @ensure_correct_data(default=(None, 'Unexpected client error'), callback=callback)
        def c(req: Request):
            if req.data["status"] == "success":
                guild = Guild.from_json_serializeable(req.data["guild"])
                callback(guild, '')
            else:
                message: str = req.data["message"]
                callback(None, message)
        
        request = Request(RequestType.JOIN_GUILD, {"code": code})
        self.request_manager.request(request, callback=c)
        
    
    def get_attachment_file(self, attachment_id: int, callback: Callable[[bytes | None, str], None]):
        @ensure_correct_data(default=(None, 'Unexpected client error'), callback=callback)
        def c(req: Request):
            if req.data["status"] == "success":
                b64_file: str = req.data["file"]
                file = base64.b64decode(b64_file)
                callback(file, '')
            else:
                message: str = req.data["message"]
                callback(None, message)
            
        request = Request(RequestType.GET_ATTACHMENT_FILE, {"attachment_id": attachment_id})
        self.request_manager.request(request, callback=c)
        
    def upload_attachment(self, attachment: Attachment, blob: bytes, callback: Callable[[Attachment | None, str], None]):
        @ensure_correct_data(default=(None, None, 'Unexpected client error'), callback=callback)
        def c(req: Request):
            if req.data["status"] == "success":
                attachment = Attachment.from_json_serializeable(req.data["attachment"])
                callback(attachment, '')
            else:
                message: str = req.data["message"]
                callback(None, message)
        
        b64_blob = base64.b64encode(blob).decode()
        request = Request(RequestType.UPLOAD_ATTACHMENT, {"filename": attachment.filename, "type": attachment.a_type.value, "file": b64_blob})
        self.request_manager.request(request, callback=c)
    
    def close(self):
        logger.debug("Closing client")
        self.sock.close() 
        self.request_manager.stop()
        logger.debug("Closed client")

    def send(self, request: Request, callback: Callable | None = None):
        self.request_manager.request(request, callback if callback else self.default_callback)
        
    def default_callback(self, req: Request):
        print(req)