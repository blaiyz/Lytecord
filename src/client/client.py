import ssl
import socket

from src.shared.protocol import HOST
from src.shared.request import Request, RequestType
from src.client.request_manager import RequestManager
from src.shared.channel import Channel, ChannelType

class Client():
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        # Deal with certificate verification later
        self.context = ssl._create_unverified_context()
        self.sock = self.context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname=self.ip)
        self.sock.connect((self.ip, self.port))
        self.request_manager = RequestManager(self.sock)
        self.request_manager.begin()
        
        
    def authenticate(self, username: str, password: str):
        self.sock.sendall(f"Authenticate {username} {password}".encode())
        res = self.sock.recv(1024).decode()
        if res == "Authenticated":
            return True
        return False
    
    def send(self, request: Request):
        self.request_manager.add_request(request)
    
    
if __name__ == "__main__":
    client = Client(*HOST)
    client.send(Request(RequestType.AUTH, Channel(123, "test", ChannelType.TEXT, 123)))
    #client.sock.close()
    print("Done")