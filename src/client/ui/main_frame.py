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

        self.client: Client = client

        self.message_manager: MessageManager = MessageManager(client=client)
        self.channel_box: ChannelBox = ChannelBox(self, message_manager=self.message_manager, client=client)
        self.channel_box.grid(row=1, column=1, sticky="nsew", padx=0, pady=0)

        self.side_panel: SidePanel = SidePanel(self, corner_radius=0, fg_color=SIDE_PANEL_FG_COLOR, channel_box=self.channel_box,
                                    client=client)
        self.side_panel.grid(row=1, column=0, sticky="nsew")

    def load(self):
        self.side_panel.load()

    def unload(self):
        self.side_panel.unload()


class SidePanel(CTkFrame):
    def __init__(self, *args, channel_box: ChannelBox, client: Client, **kwargs):
        super().__init__(*args, width=SIDE_PANEL_WIDTH, **kwargs)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, minsize=300)

        self.channel_box = channel_box
        self.client = client

        self.channels_frame: ChannelsFrame = ChannelsFrame(self, channel_box=self.channel_box, client=self.client, width=200)
        self.channels_frame.grid(row=0, column=1, sticky="nsew")

        self.guilds_frame: GuildsFrame = GuildsFrame(self, channels_frame=self.channels_frame, client=self.client)
        self.guilds_frame.grid(row=0, column=0, sticky="nsew")

    def load(self):
        self.guilds_frame.load()
        self.channels_frame.update_user()

    def unload(self):
        self.guilds_frame.clear_guilds()
        self.channels_frame.clear_channels()
