import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkFont, CTkScrollableFrame
import tkinter as tk
from PIL import Image
from loguru import logger

from src.client.client import Client
from src.client.ui.channel_button import ChannelButton
from src.client.ui.channel_box import ChannelBox
from src.shared.channel import Channel
from src.shared.guild import Guild



class ChannelsFrame(CTkScrollableFrame):
    def __init__(self, *args, channel_box: ChannelBox, client: Client, **kwargs):
        super().__init__(*args, corner_radius=0, fg_color="transparent", **kwargs)

        self._current_guild: Guild | None = None
        self._cb = channel_box
        self.client = client
        self.grid_columnconfigure(0, weight=1)
        self._loading = False

        
        self._channels: list[ChannelButton] = []

    def add_channel(self, c: Channel):
        logger.debug(f"Adding channel {c}")
        channel_button = ChannelButton(self, channel_box=self._cb, channel=c, client=self.client)
        channel_button.grid(row=len(self._channels), column=0, sticky="ew", padx=5, pady=5)
        self._channels.append(channel_button)

    def clear_channels(self):
        logger.debug(f"Clearing channels")
        
        self._cb.set_channel(None)
        for channel in self._channels:
            channel.destroy()
        self._channels.clear()
        
        
    def load(self, new_guild: Guild) -> bool:
        if new_guild == None:
            logger.warning("Cannot load channels for None guild")
            return False
        
        if self._loading:
            logger.warning("Already loading channels")
            return False
        
        self._current_guild = new_guild
        self.clear_channels()
        
        def callback(channels: list[Channel]):
            for channel in channels:
                self.add_channel(channel)
            self._loading = False
    
        self.client.get_channels(guild_id=self._current_guild.id, callback=callback)
        self._loading = True
        return True
        
    def unload(self):
        self.clear_channels()