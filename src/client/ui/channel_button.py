import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkFont, CTkScrollableFrame
from loguru import logger
from PIL import Image

from src.client.ui.channel_box import ChannelBox
from src.shared.channel import Channel


HEIGHT = 40

class ChannelButton(CTkButton):
    def __init__(self, *args, channel: Channel, channel_box: ChannelBox, **kwargs):
        super().__init__(*args, text=channel.name, command=self.on_click, font=("", 20), corner_radius=5, height=HEIGHT, **kwargs)

        self._channel = channel
        self._cb = channel_box

    @property 
    def channel(self):
        return self._channel
    
    def on_click(self):
        logger.debug(f"ChannelButton {self._channel} clicked")
        self._cb.set_channel(self._channel)
        