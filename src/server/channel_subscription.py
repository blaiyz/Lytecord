from __future__ import annotations
import threading

from loguru import logger

from src.server import message_publisher
from src.server import client
from src.shared.channel import Channel
from src.shared.message import Message
from src.shared.protocol import RequestWrapper
from src.shared.request import Request, RequestType


class ChannelSubscription():
    """ 
    Handles the subscription of a client to a channel.
    
    Runs in a separate thread to send messages to the client.
    """
    def __init__(self, client: client.Client, subscription_id: int, channel: Channel):
        self.client = client
        # This is NOT the channel id, but the subscription id
        self._id: int = subscription_id
        self.channel: Channel = channel
        self.publisher: message_publisher.MessagePublisher | None = None
        self._last_message_id: int = 0
        self._stop: bool = False
        self._thread: threading.Thread = threading.Thread(target=self._run, daemon=True)
        self._thread.name = f"Channel subscription thread {client.name}"
        self._condition: threading.Condition = threading.Condition()
        self._startup_event: threading.Event = threading.Event()

    def begin(self, publisher: message_publisher.MessagePublisher, last_message_id: int = 0):
        if not self._stop and not self._startup_event.is_set():
            self._last_message_id = last_message_id
            self._thread.start()
            self.publisher = publisher
            # Wait for the thread to start, to avoid race conditions
            self._startup_event.wait()

    def stop(self):
        with self._condition:
            self._stop = True
            self.publisher = None
            self._condition.notify()
        self._thread.join()

    def _run(self):
        with self._condition:
            self._startup_event.set()
            while not self._stop:
                # Wait for the publisher to wake up the thread
                self._condition.wait()
                if self._stop:
                    break

                if not self.publisher:
                    continue

                messages = self.publisher.get_messages(self._last_message_id)
                if len(messages) == 0:
                    continue

                # Send each message in a separate response
                for message in messages[::-1]:
                    self.client.add_response(self.create_response(message))
                self._last_message_id = messages[0].id if len(messages) > 0 else self._last_message_id

    def create_response(self, message: Message) -> RequestWrapper:
        """
        Create a response for the given message.
        """
        request = Request(RequestType.CHANNEL_SUBSCRIPTION, {"message": message})
        wrapped = RequestWrapper(request, self._id, None, True)
        return wrapped

    def wake_up(self):
        """
        Wake up the subscription thread.
        """
        with self._condition:
            self._condition.notify()

    def send_message(self, message: Message):
        """
        Send a message to the channel.
        Notifies the publisher to broadcast the message.
        """
        if not self.publisher:
            logger.warning("Tried to send message to None channel, please set publisher first")
            return False

        self._last_message_id = message.id
        self.publisher.broadcast(message, self)
        return True
