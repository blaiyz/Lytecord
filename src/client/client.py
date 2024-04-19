import ssl
import socket



class Client():
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        # Deal with certificate verification later
        self.context = ssl._create_unverified_context()
        self.sock = self.context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname=self.ip)
        self.sock.connect((self.ip, self.port))
        
        
    def authenticate(self, username: str, password: str):
        self.sock.sendall(f"Authenticate {username} {password}".encode())
        res = self.sock.recv(1024).decode()
        if res == "Authenticated":
            return True
        return False