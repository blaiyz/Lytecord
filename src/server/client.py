from ssl import SSLSocket
import asyncio

from src.shared import *
from src.shared import protocol
from src.server.request_handler import handle_request



class Client():
    def __init__(self, socket: SSLSocket):
        self.socket = socket
        self.user: User | None = None
        
    def run(self):
        asyncio.run(self.main_handler())
        
    async def _set_user(self, user: User):
        self.user = user
        
    async def main_handler(self):
        stop = False
        # Create a Future for receiving a request
        loop = asyncio.get_event_loop()
        receive_future = asyncio.ensure_future(protocol.async_receive(self.socket))

        # Create a Future for the event you're waiting for
        event_future = asyncio.ensure_future(self.wait_for_event())
        while not stop:
            try:
                # Wait for either Future to complete
                done, _ = await asyncio.wait(
                    [receive_future, event_future],
                    return_when=asyncio.FIRST_COMPLETED
                )

                responses: list[asyncio.Future[protocol.RequestWrapper]] = []
                # If the receive_future is done, handle the request
                if receive_future in done:
                    req, id, subbed = receive_future.result()
                    responses.append(handle_request(req, id, subbed, self))
                    receive_future = asyncio.ensure_future(protocol.async_receive(self.socket))

                # If the event_future is done, handle the event
                if event_future in done:
                    event = event_future.result()
                    responses.append(self.handle_event(event))
                    event_future = asyncio.ensure_future(self.wait_for_event())
                    
                for response in responses:
                    await protocol.async_send(await response, self.socket)

            except Exception as e:
                print(e)
                stop = True
                try:
                    self.socket.close()
                except:
                    pass

    async def wait_for_event(self):
        # This method should wait for the event and return it
        pass

    async def handle_event(self, event):
        # This method should handle the event
        return "test"
