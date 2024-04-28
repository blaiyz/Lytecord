from __future__ import annotations
import enum
import json
import ijson
import io
from collections.abc import Callable

from src.shared.abs_data_class import AbsDataClass, Encoder, Serializeable
import src.shared.request as request

class RequestType(enum.Enum):
    AUTHENTICATION = "Authenticate"
    REGISTER  = "Register"
    UNAUTHORIZED = "Unauthorized"
    ERROR = "Error"
    GET_MESSAGES = "GetMessages"
    SEND_MESSAGE = "SendMessage"
    CHANNEL_SUBSCRIPTION = "ChannelSubscription"
    GET_GUILDS = "GetGuilds"
    GET_CHANNELS = "GetChannels"
    GET_ASSET = "GetAsset"
    

class Request():
    def __init__(self, request_type: RequestType, data: dict | Serializeable, callback: Callable[[Request], None] | None = None):
        self.request_type = request_type
        self.data = data if isinstance(data, dict) else data.to_json_serializeable()
        
        
    
    def __str__(self):
        return f"Request({self.request_type}, {self.data})"
    
    def serialize(self):
        return f"{str(self.request_type.value)}\n{json.dumps(self.data, cls=Encoder, separators=(',', ':'))}"
        

    @staticmethod
    def deserialize(string: str)-> "Request":
        request_type, data = string.split("\n", maxsplit=1)
        data = json.loads(data)
        if isinstance(data, dict):
            return Request(RequestType(request_type), data)
        raise ValueError(f"Invalid data (got: {data})")