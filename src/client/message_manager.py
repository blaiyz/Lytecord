from datetime import datetime
import bisect
from collections.abc import Callable
from loguru import logger

from src.shared.channel import Channel
from src.shared.message import Message, TAG_BIT_LENGTH

TEST_MESSAGE = """Test message abcdefghijklmnopqrstuvwxyz 123123123123983475094387520862314912
test test
test
sussy"""

THRESHOLD = 30

class MessageManager():
    """
    This class is basically the message interface between channel_box and networking,
    which manages sending and receiving messages, and updating channel_box.
    It saves messages in a list and allows channel_box to take batches
    of messages from it, to improve performance.
    """
    def __init__(self, client):
        # Client will be the networking class
        self._client = client
        self._current_channel: Channel | None = None
        self._messages: list[Message] = []
        self.new_message_callback: Callable | None = None
        # Flag of whether reached the top of the channel (loaded all possible messages)
        self._top: bool = False
        
    def set_channel(self, channel: Channel | None):
        if channel == self._current_channel:
            return
        self._messages.clear()
        self._channel = channel
        self._top = False
        if channel is not None:
            self.fetch_messages()
        
    
    def fetch_messages(self, from_id: int = 0, count: int = 100):
        """
        Fetch messages from the server.
        
        If from_id is 0, fetches messages from the top.
        Fetches all the messages sent before the id.
        """
        if self._channel is None:
            logger.warning("Tried to fetch messages from None channel, please set channel first")
            return
        
        # Not implemented yet
        self._top = True
        for i in range(1, 150):
            t = int(datetime.now().timestamp())
            self.insert_sorted(Message(t << TAG_BIT_LENGTH + i, self._channel.id, f"TEST {i}", 1, 1, t))
        
        #logger.debug("\n" + "\n".join([str(m) for m in self._messages]))
        
            
    def get_messages(self, id: int, before = True, count: int = THRESHOLD - 5) -> list[Message]:
        """
        Used by channel_box to load more messages.
        
        If before is True, returns messages before (not including) `id`, otherwise after (not including).
        If id is 0, returns the latest messages (`before` is ignored in this case).
        
        Internally, tries to fetch more messages if the user is getting close to the top.
        Another call may be needed to get the messages.
        """
        if self._channel is None:
            logger.warning("Tried to get messages from None channel, please set channel first")
            return []
        if count <= 0:
            logger.warning("Tried to get 0 or less messages")
            return []
        
        if id == 0:
            return self._messages[0:count]
        else:
            if not before:
                # If trying to get messages after the latest message
                if self._messages[0].id <= id:
                    return []
                
                # PLEASE DO NOT REMOVE THE MINUS
                # IT TOOK ME WAY TOO LONG TO DEBUG
                index = bisect.bisect_left(self._messages, -id, key=lambda x: x.sort_key())
                logger.debug(f"Index: {index}, i-c: {max(index - count, 0)}")
                return self._messages[max(index - count, 0):index]
            
            # If trying to get messages before the oldest message (that is currently fetched)
            if self._messages[-1].id >= id:
                ret = []
            else:
                #logger.debug(f"id: {id}, Messages\n" + "\n".join([str(m) for m in self._messages]))
                
                # PLEASE DO NOT REMOVE THE MINUS
                index = bisect.bisect_right(self._messages, -id, key=lambda x: x.sort_key())
                logger.debug(f"Index: {index}, i+c: {min(index + count, len(self._messages))}")
                ret = self._messages[index:min(index + count, len(self._messages))]
            
            # If the user is getting close or reached the top, fetch more messages
            if not self._top and (len(self._messages) - (index + count) < THRESHOLD or ret == []):
                self.fetch_messages(from_id= self._messages[-1].id)
            
            return ret
            
    def insert_sorted(self, message: Message):
        if self._messages is None:
            logger.warning("Tried to insert message into None message list, please set channel first")
            return
        
        if message not in self._messages:
            bisect.insort(self._messages, message, key=lambda x: x.sort_key())
            
    def send_message(self, message: Message):
        if self._channel is None:
            logger.warning("Cannot send message in a None channel, please set channel first")
            return
        
        # Implement networking later
        # should ask the server to send the message and then call new_message (probably on a different thread)
        t = int(datetime.now().timestamp())
        self.new_message(Message(t << TAG_BIT_LENGTH, self._channel.id, message.content, 1, 1, t))
    
    def new_message(self, message: Message):
        if self._messages is None:
            logger.warning("Cannot send message in a None channel, please set channel first")
            return
        
        logger.info(f"New message: {message}")
        self.insert_sorted(message)
        if self.new_message_callback is not None:
            self.new_message_callback(message)
            
    