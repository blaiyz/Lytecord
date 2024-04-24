from loguru import logger
import threading
import bisect

from src.server.channel_subscription import ChannelSubscription
from src.shared.channel import Channel
from src.shared.message import Message

BUFFER_SIZE = 100

class ServerChannel:
    def __init__(self, channel: Channel):
        self.channel = channel
        self._lock = threading.Lock()
        self._subscriptions: list[ChannelSubscription] = []
        self._buffer: list[Message] = []
        
    def add_subscription(self, sub: ChannelSubscription):
        with self._lock:
            self._subscriptions.append(sub)
            
    def remove_subscription(self, sub: ChannelSubscription):
        with self._lock:
            self._subscriptions.remove(sub)
            
    def is_empty(self):
        with self._lock:
            return len(self._subscriptions) == 0
            
    def broadcast(self, message: Message, sender: ChannelSubscription):
        with self._lock:
            if message in self._buffer:
                return
            
            bisect.insort(self._buffer, message, key=lambda x: x.sort_key())
            if len(self._buffer) > BUFFER_SIZE:
                self._buffer.pop()
            for sub in self._subscriptions:
                if sub != sender:
                    sub.wake_up()
                    
    def get_messages(self, after: int):
        """
        Return messages after the given id
        """
        with self._lock:
            if self.is_empty():
                return []
            
            if self._buffer[0].id >= after:
                return []
            
            index = bisect.bisect_left(self._buffer, -after, key=lambda x: x.sort_key())
            return self._buffer[:index]
            
        
lock = threading.Lock()

channels: dict[int, ServerChannel] = {}

def subscribe(client: ChannelSubscription):
    channel_id = client.channel.id
    with lock:
        if channel_id not in channels:
            channels[channel_id] = ServerChannel(client.channel)
        channels[channel_id].add_subscription(client)
        
    return channels[channel_id]
        
        
def unsubscribe(client: ChannelSubscription):
    channel_id = client.channel.id
    with lock:
        if channel_id in channels:
            channels[channel_id].remove_subscription(client)
            if channels[channel_id].is_empty():
                del channels[channel_id]
                
def get_channel(id: int):
    with lock:
        return channels.get(id, None)