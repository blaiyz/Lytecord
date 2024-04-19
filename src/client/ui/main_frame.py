import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkFont, CTkScrollableFrame
from PIL import Image

from src.client.ui.channel_box import ChannelBox
from src.client.ui.channels_frame import ChannelsFrame
from src.client.ui.guilds_frame import GuildsFrame
from src.client.message_manager import MessageManager

SIDE_PANEL_FG_COLOR = "#26263b"

SIDE_PANEL_WIDTH = 300
GUILD_ICON_SIZE = 50

class MainFrame(CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, fg_color="transparent", **kwargs)


        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.current_channel = None

        self.mm = MessageManager(None)
        self.cb = ChannelBox(self, message_manager=self.mm, client=None)
        self.cb.grid(row=1, column=1, sticky="nsew", padx=0, pady=0)

        self.side_panel = SidePanel(self, corner_radius=0, fg_color=SIDE_PANEL_FG_COLOR, channel_box=self.cb)
        self.side_panel.grid(row=1, column=0, sticky="nsew")


class SidePanel(CTkFrame):
    def __init__(self, *args, channel_box: ChannelBox, **kwargs):
        super().__init__(*args, width=SIDE_PANEL_WIDTH, **kwargs)

        self.grid_rowconfigure(0, weight=1)

        self.channel_box = channel_box

        self.cf = ChannelsFrame(self, channel_box=self.channel_box)
        self.cf.grid(row=0, column=1, sticky="nsew")

        self.gf = GuildsFrame(self, cf=self.cf)
        self.gf.grid(row=0, column=0, sticky="nsew")
