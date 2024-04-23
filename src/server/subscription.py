import threading

from src.server.client import Client

class Subscription():
    def __init__(self, client: Client, id: int, condition: threading.Condition):
        self.client = client
        self.id = id
        self.stop = False
        self.condition = condition