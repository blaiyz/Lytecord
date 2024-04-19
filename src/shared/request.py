import enum
import json
from collections.abc import Callable

from src.shared.abs_data_class import AbsDataClass

class RequestType(enum.Enum):
    AUTH = "Authenticate"
    GET_MESSAGES = "GetMessages"
    SEND_MESSAGE = "SendMessage"
    GET_GUILDS = "GetGuilds"
    GET_CHANNELS = "GetChannels"
    GET_ASSET = "GetAsset"
    
class Encoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, AbsDataClass):
            return o.serialize(o)
        return o.__dict__

class Request():
    def __init__(self, request_type: RequestType, data: dict, callback: Callable | None = None):
        self.request_type = request_type
        self.data = data
        self.callback = callback
        
        
    def serialize(self):
        return f"{self.request_type}\n{json.dumps(self.data, cls=Encoder, separators=(',', ':'))}"
        
        
    @staticmethod
    def deserialize(string: str)-> "Request":
        request_type, data = string.split("\n", maxsplit=1)
        return Request(RequestType(request_type), json.loads(data))