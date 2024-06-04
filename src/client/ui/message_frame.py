import tkinter as tk
from datetime import datetime, timedelta

import customtkinter as ctk
from customtkinter import (CTkButton, CTkEntry, CTkFont, CTkFrame, CTkLabel,
                           CTkTextbox)
from loguru import logger

from src.client.client import Client
from src.client.ui.loadable_image import LoadableImage
from src.shared.message import Message

FONT_SIZE = 14

MAX_DISPLAYED_IMAGE_WIDTH = 700
MAX_DISPLAYED_IMAGE_HEIGHT = 300


def pretty_relative_date(d: datetime) -> str:
    today = datetime.now().date()
    date = d.date()

    if date == today:
        return 'today'
    elif date == today - timedelta(days=1):
        return 'yesterday'
    elif date > today - timedelta(days=7):
        return f'{(today - date).days} days ago'
    else:
        return d.strftime('%d/%m/%Y')


class MessageFrame(CTkFrame):
    FONT = None

    def __init__(self, *args, message: Message, client: Client, **kwargs):
        super().__init__(*args, **kwargs)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.message = message
        self._client = client
        self._author_name = message.author.username
        self._author_name_color = message.author.name_color
        self._author_label = CTkLabel(self, text=self._author_name, font=CTkFont(size=FONT_SIZE + 2, weight="bold"),
                                      text_color=self._author_name_color)
        self._author_label.grid(row=0, column=0, sticky="w", padx=10, pady=1)

        time = datetime.fromtimestamp(self.message.timestamp)
        self._time_label = CTkLabel(self, text=time.strftime("%H:%M,  ") + pretty_relative_date(time),
                                    font=CTkFont(size=FONT_SIZE - 2), text_color="#888888")
        self._time_label.grid(row=0, column=1, sticky="nsw", padx=10, pady=2)

        # Use label for now, change to textbox later if possible
        if MessageFrame.FONT is None:
            MessageFrame.FONT = CTkFont(size=FONT_SIZE)

        self._content_label = CTkLabel(self, text=self.message.content, font=MessageFrame.FONT, justify="left",
                                       anchor="w", wraplength=500, pady=4)
        self._content_label.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=(1, 10))

        if self.message.attachment is not None:
            self._image_frame = LoadableImage(self, image=self.message.attachment, corner_radius=10,
                                              client=self._client, max_width=MAX_DISPLAYED_IMAGE_WIDTH,
                                              max_height=MAX_DISPLAYED_IMAGE_HEIGHT)
            self._image_frame.grid(row=2, column=0, columnspan=2, sticky='w', padx=10, pady=(0, 10))

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

    def load_attachment(self, delay: int | None = None) -> int:
        if self.message.attachment is not None:
            size = self.message.attachment.size
            relative_delay = round(size * 0.0003)
            if not delay:
                self._image_frame.load()
                return relative_delay
            self._image_frame.load(self.after, delay)
            return relative_delay
        return 0
