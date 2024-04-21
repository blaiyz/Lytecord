import ssl
import socket
from typing import Callable

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
        
        
    def authenticate(self, username: str, password: str):
        self.sock.sendall(f"Authenticate {username} {password}".encode())
        res = self.sock.recv(1024).decode()
        if res == "Authenticated":
            return True
        return False
    
    
    # 
    def send(self, request: Request, callback: Callable | None = None):
        self.request_manager.request(request, callback if callback else self.default_callback)
        
    def default_callback(self, req: Request):
        print(req)
    
    
if __name__ == "__main__":
    client = Client(*HOST)
    client.send(Request(RequestType.AUTH, Channel(123, "test", ChannelType.TEXT, 123)))
    print("Done")