from customtkinter import CTkFont, CTkFrame, CTkLabel
from loguru import logger

from src.client.client import Client
from src.client.message_manager import MessageManager
from src.client.ui.text_channel import TextChannel
from src.shared.channel import Channel

COLOR = ("#ebebeb", "#252525")


class ChannelBox(CTkFrame):
    """
    Houses the frames for different channel types
    """

    def __init__(self, *args, message_manager: MessageManager, client: Client, **kwargs):
        super().__init__(*args, corner_radius=0, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._channel: Channel | None = None
        self._client = client

        self._text_channel: TextChannel = TextChannel(self, message_manager=message_manager, client=client)
        self._text_channel.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

        # Empty channel frame
        self._empty_channel = CTkFrame(self, fg_color=COLOR, corner_radius=0)
        self._empty_channel.grid_columnconfigure(0, weight=1)
        self._empty_channel.grid_rowconfigure(0, weight=1)
        self._empty_channel_label = CTkLabel(self._empty_channel, text="No channel selected",
                                             font=CTkFont(family="Helvetica", size=50), fg_color="transparent",
                                             text_color=("#171717", "#636363"))
        self._empty_channel_label.grid(row=0, column=0, sticky="nsew")
        self._empty_channel.grid(row=0, column=0, sticky="nsew")

    def set_channel(self, channel: Channel | None) -> bool:
        logger.info(f"Setting channel; new: {channel}, old: {self._channel}")
        if self._channel == channel:
            if channel is not None:
                logger.warning("Tried to set the same channel")
                return False
            return True

        success = self._text_channel.set_channel(channel)
        if not success:
            return False

        if channel is None:
            self._text_channel.grid_remove()
            self._empty_channel.grid()
        else:
            self._empty_channel.grid_remove()
            self._text_channel.grid()
        self._channel = channel
        return True
