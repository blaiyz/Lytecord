import ssl
import socket
from typing import Callable
from loguru import logger
from functools import wraps

from src.shared.protocol import HOST
from src.shared import *
from src.client import RequestManager



def ensure_correct_data(default, callback: Callable):
    def outer(func: Callable[[Request], None]):
        @wraps(func)
        def inner(req: Request):
            try:
                func(req)
            except (TypeError, ValueError):
                logger.debug(f"Invalid data: {req.data} from func: {func.__name__}")
                callback(default)
        return inner
    return outer

class Client():
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        # Deal with certificate verification later
        self.context = ssl._create_unverified_context()
        self.sock = self.context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname=self.ip)
        self.sock.connect((self.ip, self.port))
        self.sock.setblocking(True)
        self.request_manager = RequestManager(self.sock)
        self.request_manager.begin()
        self.current_channel: Channel | None = None
        
        
    def authenticate(self, username: str, password: str, callback: Callable[[bool], None]):
        @ensure_correct_data(default=False, callback=callback)
        def c(req: Request):
            if req.data["status"] == "success" and req.data["message"] == "Authenticated":
                callback(True)
            callback(False)
        
        request = Request(RequestType.AUTHENTICATION, {"username": username, "password": password}, callback=c)
        self.request_manager.request(request, callback=c)
        
    def get_guilds(self, callback: Callable[[list[Guild]], None]):
        @ensure_correct_data(default=[], callback=callback)
        def c(req: Request):
            if req.data["status"] == "success":
                guilds = [Guild.from_dict(guild) for guild in req.data["guilds"]]
                callback(guilds)
            else:
                callback([])
        
        request = Request(RequestType.GET_GUILDS, {}, callback=c)
        self.request_manager.request(request, callback=c)
        
    def get_channels(self, guild_id: int, callback: Callable[[list[Channel]], None]):
        @ensure_correct_data(default=[], callback=callback)
        def c(req: Request):
            if req.data["status"] == "success":
                channels = [Channel.from_dict(channel) for channel in req.data["channels"]]
                callback(channels)
            else:
                callback([])
        
        request = Request(RequestType.GET_CHANNELS, {"guild_id": guild_id}, callback=c)
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
    

    
if __name__ == "__main__":
    client = Client(*HOST)
    client.send(Request(RequestType.AUTHENTICATION, Channel(123, "test", ChannelType.TEXT, 123)))
    print("Done")