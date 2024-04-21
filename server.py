import socket, ssl

from src.shared.protocol import HOST, RequestWrapper
from src.shared.channel import Channel, ChannelType
from src.shared import protocol, Request, RequestType, AbsDataClass, Serializeable





def client_handler(client: ssl.SSLSocket, addr: tuple[str, int]):
    pass




def main():
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")
    bindsocket = socket.socket()
    bindsocket.bind(HOST)
    bindsocket.listen(5)
    
    
    while True:
        sock, addr = bindsocket.accept()
        client = context.wrap_socket(sock, server_side=True)
        # Just a test
        request, id, subbed = protocol.receive(client)
        print(request, id, subbed)
        assert type(request.data) == dict
        data: dict = request.data
        channel_id = data["id"]
        name = data["name"]
        channel_type = ChannelType(data["type"])
        guild_id = data["guild_id"]
        chnl = Channel(channel_id, name, channel_type, guild_id)
        print(chnl)
        protocol.send(RequestWrapper(Request(RequestType.AUTH, chnl), id, None), client)
        
        
if __name__ == "__main__":
    main()