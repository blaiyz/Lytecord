import customtkinter as ctk
from customtkinter import (CTkButton, CTkEntry, CTkFont, CTkFrame, CTkLabel,
                           CTkScrollableFrame)
from PIL import Image

from src.client.client import Client
from src.client.message_manager import MessageManager
from src.client.ui.channel_box import ChannelBox
from src.client.ui.channels_frame import ChannelsFrame
from src.client.ui.guilds_frame import GuildsFrame

SIDE_PANEL_FG_COLOR = "#26263b"

SIDE_PANEL_WIDTH = 300
GUILD_ICON_SIZE = 50

class MainFrame(CTkFrame):
    def __init__(self, *args, client: Client, **kwargs):
        super().__init__(*args, fg_color="transparent", **kwargs)


        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.client = client

        self.mm = MessageManager(client=client)
        self.cb = ChannelBox(self, message_manager=self.mm, client=client)
        self.cb.grid(row=1, column=1, sticky="nsew", padx=0, pady=0)

        self.side_panel = SidePanel(self, corner_radius=0, fg_color=SIDE_PANEL_FG_COLOR, channel_box=self.cb, client=client)
        self.side_panel.grid(row=1, column=0, sticky="nsew")
        
    def load(self):
        self.side_panel.load()
        
    def unload(self):
        self.side_panel.unload()


class SidePanel(CTkFrame):
    def __init__(self, *args, channel_box: ChannelBox, client: Client, **kwargs):
        super().__init__(*args, width=SIDE_PANEL_WIDTH, **kwargs)

        self.grid_rowconfigure(0, weight=1)

        self.channel_box = channel_box
        self.client = client

        self.cf = ChannelsFrame(self, channel_box=self.channel_box, client=self.client)
        self.cf.grid(row=0, column=1, sticky="nsew")

        self.gf = GuildsFrame(self, channels_frame=self.cf, client=self.client)
        self.gf.grid(row=0, column=0, sticky="nsew")

    def load(self):
        self.gf.load()
        
    def unload(self):
        self.gf.clear_guilds()
        self.cf.clear_channels()