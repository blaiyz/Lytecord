import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkFont, CTkScrollableFrame, CTkImage, CTkInputDialog
from CTkMessagebox import CTkMessagebox
import tkinter as tk
from PIL import Image
from loguru import logger

from src.client.client import Client
from src.client.ui.channel_button import ChannelButton
from src.client.ui.channel_box import ChannelBox
from src.client.ui.design import CREATE_GUILD_ICON_DARK, CREATE_GUILD_ICON_LIGHT, REFRESH_ICON_DARK, REFRESH_ICON_LIGHT
from src.shared.channel import Channel, ChannelType, MIN_NAME_LENGTH, MAX_NAME_LENGTH
from src.shared.guild import Guild


FG_COLOR = ("#8e8e8e", "#353535")


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

        font = CTkFont(size=20)
        self._scroll_frame = CTkScrollableFrame(self, fg_color="transparent", scrollbar_fg_color="transparent", label_fg_color=FG_COLOR, label_font=font)
        self._scroll_frame.grid_columnconfigure(0, weight=1)
        self._scroll_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self._scroll_frame.grid_remove()
        
        icon = CTkImage(light_image=CREATE_GUILD_ICON_LIGHT, dark_image=CREATE_GUILD_ICON_DARK, size=(20, 20))
        self._create_channel_button = CTkButton(self, text="Create Channel", image=icon, corner_radius=5, fg_color=FG_COLOR, hover_color="#727272", command=self.on_create_channel, font=font)
        self._create_channel_button.grid(row=2, column=0, sticky="ew", padx=5, pady=(5, 5))
        self._create_channel_button.grid_remove()
        
        self._guild_code_frame = CTkFrame(self, corner_radius=5, fg_color="transparent")
        self._guild_code_frame.grid(row=3, column=0, sticky="ew", padx=0, pady=(5, 15))
        self._guild_code_frame.grid_remove()
        self._guild_code_frame.grid_columnconfigure(0, weight=1)
        entry_font = CTkFont(weight="bold", size=15)
        self._guild_code_entry = CTkEntry(self._guild_code_frame, fg_color=FG_COLOR, font=entry_font, state="readonly")
        self._guild_code_entry.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        icon = CTkImage(light_image=REFRESH_ICON_LIGHT, dark_image=REFRESH_ICON_DARK, size=(20, 20))
        self._guild_code_button = CTkButton(self._guild_code_frame, text="", image=icon, corner_radius=5, fg_color=FG_COLOR, hover_color="#727272", command=self.refresh_guild_code, width=20, height=20)
        self._guild_code_button.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        

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
        
    def center_top_level(self, top_level: ctk.CTkToplevel):
        root = self.winfo_toplevel()
        x = int(root.winfo_width() * .5 + self.winfo_rootx() - .5 * top_level.winfo_width())
        y = int(root.winfo_height() * .5 + self.winfo_rooty() - .5 * top_level.winfo_height())
        top_level.geometry(f"+{x}+{y}")  
        
    def on_create_channel(self):
        if self._current_guild is None:
            logger.warning("No guild selected")
            return
        
        dialog = CTkInputDialog(title="Create Channel", text="Enter the name of the new channel")
        self.center_top_level(dialog)

        name = dialog.get_input()
        logger.debug(f"Creating channel with name {name}")
        
        if name is None:
            return
        
        name = name.lower().replace(" ", "-")

        message = None
        if len(name) > MAX_NAME_LENGTH:
            message = f"Name cannot be more than {MAX_NAME_LENGTH} characters long"
        elif len(name) < MIN_NAME_LENGTH:
            message = f"Name cannot be less than {MIN_NAME_LENGTH} characters long"
        elif not name.islower():
            message = "Name must be all lowercase"
        else:
            try:
                channel = Channel(0, name, ChannelType.TEXT, 0)
            except:
                message = "Name may only contain lowercase letters, numbers, and hyphens"
        
        if message:
            box = CTkMessagebox(title="Create Channel", message=message, icon="cancel", option_1="Ok", option_2="Retry")
            self.center_top_level(box)
            
            response = box.get()
            if response == "Retry":
                self.after_idle(self.on_create_channel)
            return
        
        
        def callback(channel: Channel | None, message: str):
            if channel is not None:
                if self._current_guild is not None and channel.guild_id == self._current_guild.id:
                    self.add_channel(channel)
                box = CTkMessagebox(title="Create Channel", message=f"Successfully created channel with name \"{channel.name}\"", icon="check", option_1="Ok")
                self.center_top_level(box)
                return
            
            box = CTkMessagebox(title="Create Channel", message="Error at creating channel: " + message, icon="cancel", option_1="Ok", option_2="Retry")
            self.center_top_level(box)
            
            response = box.get()
            if response == "Retry":
                self.after_idle(self.on_create_channel)
        
        self.client.create_channel(channel.name, guild_id=self._current_guild.id, callback=callback)
        
    def refresh_guild_code(self):
        if self._current_guild is None:
            return
        
        before_guild = self._current_guild
        def callback(code: str | None):
            if self._current_guild is None:
                return
            
            if self._current_guild != before_guild:
                return
            
            if code is None:
                return
            
            self._guild_code_entry.configure(state="normal")
            self._guild_code_entry.delete(0, tk.END)
            self._guild_code_entry.insert(0, code)
            self._guild_code_entry.configure(state="readonly")

            
        self.client.refresh_guild_join_code(guild_id=self._current_guild.id, callback=callback)
        
    def load(self, new_guild: Guild) -> bool:
        if new_guild is None:
            logger.warning("Cannot load channels for None guild")
            return False
        
        if self._loading:
            logger.warning("Already loading channels")
            return False
        
        if not self._channel_box.set_channel(None):
            return False
        
        self._current_guild = new_guild
        self.clear_channels()
        
        def load_channels_callback(channels: list[Channel]):
            if self._current_guild is None:
                logger.warning("No guild selected")
                return
            
            for channel in channels:
                self.add_channel(channel)
            self._scroll_frame.configure(label_text=self._current_guild.name)
            self._scroll_frame.grid()

            self._loading = False
    
        def set_join_code(code: str | None):
            if self._current_guild is None:
                return
            
            if self._current_guild != new_guild:
                return
            
            if code is None:
                return
            
            if self.client.user is not None and self._current_guild.owner_id == self.client.user.id:
                self._guild_code_entry.configure(state="normal")
                self._guild_code_entry.delete(0, tk.END)
                self._guild_code_entry.insert(0, code)
                self._guild_code_entry.configure(state="readonly")
                logger.debug(f"code: {self._guild_code_entry.get()}")
            
    
        self._loading = True
        self._scroll_frame.grid_remove()
        self._create_channel_button.grid_remove()
        self._guild_code_frame.grid_remove()
        self._guild_code_entry.delete(0, tk.END)
        self.client.get_channels(guild_id=self._current_guild.id, callback=load_channels_callback)
        
        if self.client.user is not None and self._current_guild.owner_id == self.client.user.id:
            self.client.get_guild_join_code(guild_id=self._current_guild.id, callback=set_join_code)
            self._create_channel_button.grid()
            self._guild_code_frame.grid()
    
        return True
        
    def unload(self):
        self.clear_channels()