import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkFont, CTkTextbox
import tkinter as tk
from datetime import datetime
from loguru import logger

from src.client.client import Client
from src.shared.message import Message

FONT_SIZE = 14


class MessageFrame(CTkFrame):
    FONT = None
    def __init__(self, *args, message: Message, client: Client, **kwargs):
        super().__init__(*args, **kwargs)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.message = message
        self._client = client
        self._author_name = message.author.username # Fetching name will be implemented later
        self._author_label = CTkLabel(self, text=self._author_name, font=CTkFont(size=FONT_SIZE+2, weight="bold"))
        self._author_label.grid(row=0, column=0, sticky="w", padx=10, pady=1)

        self._time_label = CTkLabel(self, text=datetime.fromtimestamp(self.message.timestamp).strftime("%H:%M"), font=CTkFont(size=FONT_SIZE-2))
        self._time_label.grid(row=0, column=1, sticky="w", padx=10, pady=1)

        # Use label for now, change to textbox later if possible
        if MessageFrame.FONT is None:
            MessageFrame.FONT = CTkFont(size=FONT_SIZE)
        
        self._content_label = CTkLabel(self, text=self.message.content, font=MessageFrame.FONT, justify="left", anchor="w", wraplength=500, pady=4)
        self._content_label.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=(1, 10))
        

        # TODO: Implement attachments
        # Using textbox for a few reasons:
        # 1. It has word wrapping
        # 2. Allows you to select text (unlike labels for some reason)
        # For this reason, I have to do all these shenanigans to make it look like a label
        # self._border_spacing = 2
        # self._textbox_font = CTkFont(size=FONT_SIZE)
        # self._content_label = CTkTextbox(self, font=self._textbox_font, activate_scrollbars=False, fg_color="transparent", border_spacing=self._border_spacing, wrap="word", height=1)
        # self._content_label.insert("end", self._message.content)
        # self._content_label.configure(state="disabled")
        # self._reset_height()
        # self._content_label.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=4)
        
    # def _reset_height(self):
    #     height = (FONT_SIZE + 2) * (self._message.content.count("\n")) + self._border_spacing * 2
    #     self._content_label.configure(height=height)