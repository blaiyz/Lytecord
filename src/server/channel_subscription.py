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
            self._startup_event.wait()
            self.publisher = publisher

    def stop(self):
        with self._condition:
            self._stop = True
            logger.debug("got here")
            logger.debug('unsubscribed')
            self.publisher = None
            self._condition.notify()
            logger.debug('notified')
        self._thread.join()

    def _run(self):
        with self._condition:
            self._startup_event.set()
            logger.debug("event set")
            while not self._stop:
                self._condition.wait()
                logger.debug(f"woke up {self._id}, {self._stop}")
                if self._stop:
                    break

                if not self.publisher:
                    continue

                messages = self.publisher.get_messages(self._last_message_id)
                if len(messages) == 0:
                    continue

                for message in messages[::-1]:
                    self.client.add_response(self.create_response(message))
                self._last_message_id = messages[0].id if len(messages) > 0 else self._last_message_id

    def create_response(self, message: Message) -> RequestWrapper:
        request = Request(RequestType.CHANNEL_SUBSCRIPTION, {"message": message})
        wrapped = RequestWrapper(request, self._id, None, True)
        return wrapped

    def wake_up(self):
        with self._condition:
            self._condition.notify()

    def send_message(self, message: Message):
        if not self.publisher:
            logger.warning("Tried to send message to None channel, please set channel first")
            return False

        self._last_message_id = message.id
        self.publisher.broadcast(message, self)
        return True
