import threading

from src.server.client import Client
from src.shared.channel import Channel
from src.server import channel_manager
from src.shared.message import Message
from src.shared.protocol import RequestWrapper
from src.shared.request import Request, RequestType

class ChannelSubscription():
    def __init__(self, client: Client, id: int, channel: Channel):
        self.client = client
        # This is NOT the channel id, but the subscription id
        self._id = id
        self.channel = channel
        self._last_message_id = 0
        self._stop = False
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._condition = threading.Condition()
        self._startup_event = threading.Event()

    def begin(self):
        if not self._stop:
            self._thread.start()
            self._startup_event.wait()
            channel_manager.subscribe(self)

            
    def stop(self):
        self._stop = True
        with self.client._condition:
            self.client._condition.notify()
        self._thread.join()
        
    def _run(self):
        with self._condition:
            self._startup_event.set()
            while not self._stop:
                self._condition.wait()
                if self._stop:
                    break
                
                server_channel = channel_manager.get_channel(self.channel.id)
                if not server_channel:
                    continue
                
                messages = server_channel.get_messages(self._last_message_id)
                for message in messages:
                    self.client.add_response(self.create_response(message))
                    
    def create_response(self, message: Message) -> RequestWrapper:
        request = Request(RequestType.CHANNEL_SUBSCRIPTION, message)
        wrapped = RequestWrapper(request, self._id, None, True)
        return wrapped
        
                    
    def wake_up(self):
        with self._condition:
            self._condition.notify()