import enum
import json
from collections.abc import Callable

from src.shared.abs_data_class import AbsDataClass, Encoder, Serializeable

class RequestType(enum.Enum):
    AUTH = "Authenticate"
    GET_MESSAGES = "GetMessages"
    SEND_MESSAGE = "SendMessage"
    GET_GUILDS = "GetGuilds"
    GET_CHANNELS = "GetChannels"
    GET_ASSET = "GetAsset"
    

class Request():
    def __init__(self, request_type: RequestType, data: object, callback: Callable | None = None):
        self.request_type = request_type
        self.data = data
        self.callback = callback
        
        
    
    def __str__(self):
        return f"Request({self.request_type}, {self.data}, {self.callback})"
    
    def serialize(self):
        return f"{str(self.request_type.value)}\n{json.dumps(self.data, cls=Encoder, separators=(',', ':'))}"
        
        
    @staticmethod
    def deserialize(string: str)-> "Request":
        request_type, data = string.split("\n", maxsplit=1)
        return Request(RequestType(request_type), json.loads(data))