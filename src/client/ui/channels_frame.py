import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkFont, CTkScrollableFrame, CTkImage
import tkinter as tk
from PIL import Image
from loguru import logger

from src.client.client import Client
from src.client.ui.channel_button import ChannelButton
from src.client.ui.channel_box import ChannelBox
from src.client.ui.design import CREATE_GUILD_ICON_DARK, CREATE_GUILD_ICON_LIGHT
from src.shared.channel import Channel
from src.shared.guild import Guild


FG_COLOR = ("#171717", "#636363")


class ChannelsFrame(CTkFrame):
    def __init__(self, *args, channel_box: ChannelBox, client: Client, **kwargs):
        super().__init__(*args, corner_radius=0, fg_color="transparent", **kwargs)

        self._loading = False
        self._channels: list[ChannelButton] = []

        self._current_guild: Guild | None = None
        self._channel_box = channel_box
        self.client = client
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        font = CTkFont(family="Helvetica", size=20)
        self._scroll_frame = CTkScrollableFrame(self, fg_color="transparent", scrollbar_fg_color="transparent", label_fg_color=FG_COLOR, label_font=font)
        self._scroll_frame.grid_columnconfigure(0, weight=1)
        self._scroll_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self._scroll_frame.grid_remove()
        
        icon = CTkImage(light_image=CREATE_GUILD_ICON_LIGHT, dark_image=CREATE_GUILD_ICON_DARK, size=(20, 20))
        self._create_channel_button = CTkButton(self, text="Create Channel", image=icon, corner_radius=5, fg_color=FG_COLOR, hover_color="#727272", command=self.on_create_channel, font=font)
        self._create_channel_button.grid(row=2, column=0, sticky="ew", padx=5, pady=(5, 15))
        self._create_channel_button.grid_remove()

        

    def add_channel(self, c: Channel):
        logger.debug(f"Adding channel {c}")
        channel_button = ChannelButton(self._scroll_frame, channel_box=self._channel_box, channel=c, client=self.client)
        channel_button.grid(row=len(self._channels), column=0, sticky="ew", padx=5, pady=5)
        self._channels.append(channel_button)

    def clear_channels(self):
        logger.debug(f"Clearing channels")
        
        self._channel_box.set_channel(None)
        for channel in self._channels:
            channel.destroy()
        self._channels.clear()
        
        
    def on_create_channel(self):
        logger.debug("Create channel button clicked")
        
    def load(self, new_guild: Guild) -> bool:
        if new_guild == None:
            logger.warning("Cannot load channels for None guild")
            return False
        
        if self._loading:
            logger.warning("Already loading channels")
            return False
        
        if not self._channel_box.set_channel(None):
            return False
        
        self._current_guild = new_guild
        self.clear_channels()
        
        def callback(channels: list[Channel]):
            if self._current_guild is None:
                logger.warning("No guild selected")
                return
            
            for channel in channels:
                self.add_channel(channel)
            self._scroll_frame.configure(label_text=self._current_guild.name)
            self._scroll_frame.grid()
            self._create_channel_button.grid()
            self._loading = False
    
        self._scroll_frame.grid_remove()
        self._create_channel_button.grid_remove()
        self.client.get_channels(guild_id=self._current_guild.id, callback=callback)
        self._loading = True
        return True
        
    def unload(self):
        self.clear_channels()