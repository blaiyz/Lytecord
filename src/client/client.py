import ssl
import socket
from typing import Callable
from loguru import logger

from src.shared.protocol import HOST
from src.shared import Request, RequestType, Channel, ChannelType
from src.client import RequestManager

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
        
        
    def authenticate(self, username: str, password: str, callback: Callable[[bool], None]):
        def c(req: Request):
            if req.data["status"] == "success" and req.data["message"] == "Authenticated":
                callback(True)
            callback(False)
        
        request = Request(RequestType.AUTHENTICATION, {"username": username, "password": password}, callback=c)
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