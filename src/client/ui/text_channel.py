import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkFont, CTkScrollableFrame, CTkImage
import tkinter as tk
from datetime import datetime
from loguru import logger


from src.client.client import Client
from src.client.ui.message_frame import MessageFrame
from src.client.message_manager import MessageManager, THRESHOLD
from src.shared.channel import Channel, ChannelType
from src.shared.message import TAG_BIT_LENGTH, Message, MAX_MESSAGE_LENGTH
from src.client.ui.design import ATTACHMENT_ICON_DARK, ATTACHMENT_ICON_LIGHT

TEST_MESSAGE = """Test message abcdefghijklmnopqrstuvwxyz 123123123123983475094387520862314912
test test
test
sussy"""

ENTRY_COLOR = "#373737"
HOVER_COLOR = "#727272"

COLOR = ("#ebebeb", "#252525")
FONT_SIZE = 14

MIN_ROW = 10
MAX_ROW = 1000
LOAD_COUNT = THRESHOLD - 5
MIN_MESSAGES = 2 * LOAD_COUNT
MAX_MESSAGES = MIN_MESSAGES + LOAD_COUNT
DIFF = MAX_MESSAGES - MIN_MESSAGES
START_ROW = MAX_MESSAGES + MIN_ROW
MESSAGE_GRID_KWARGS = {"column":0, "sticky":"nsew", "pady":(0, 5)}


class TextChannel(CTkFrame):
    """
    Contains the channel messages and the message entry.
    """
    def __init__(self, *args, message_manager: MessageManager, client: Client, **kwargs):
        super().__init__(*args, corner_radius=0, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._mm = message_manager
        self._client = client
        self._message_list: list[MessageFrame] = []
        self._mm.new_message_callback = self.new_message
        self._top_row = START_ROW
        self._bottom_row = START_ROW + 1
        self._scroll_lock = True
        self._channel: Channel | None = None
        self._loading = False
        
        # Messages frame
        self._messages_frame = CTkScrollableFrame(self, label_anchor="n", label_text="", label_font=CTkFont(family="Helvetica", size=20), fg_color="transparent")
        self._messages_frame._parent_canvas.configure(yscrollincrement=3)
        self._messages_frame.grid_columnconfigure(0, weight=1)
        self._messages_frame.grid_rowconfigure(0, weight=1)
        self._messages_frame.bind_all("<MouseWheel>", self._scroll_callback, add=True)


        # Message entry and the attachment button
        self._entry_frame = CTkFrame(self, fg_color=ENTRY_COLOR)
        self._entry_frame.grid_columnconfigure(1, weight=1)
        
        attachment_icon = CTkImage(light_image=ATTACHMENT_ICON_LIGHT, dark_image=ATTACHMENT_ICON_DARK, size=(32, 32))
        self._attachment_button = CTkButton(self._entry_frame, text="", image=attachment_icon, bg_color=ENTRY_COLOR, fg_color=ENTRY_COLOR, corner_radius=5, width=32, height=32, hover_color=HOVER_COLOR)
        self._attachment_button.grid(row=0, column=0, sticky="nsew", padx=5, pady=3)
        
        self._entry = CTkEntry(self._entry_frame, fg_color="transparent", border_width=0, font=CTkFont(family="Helvetica", size=18), corner_radius=5, validate="key", validatecommand=(self.master.register(self._character_limit), '%d', '%P')) 
        self._entry.bind("<Return>", self._send_message)
        
        self._messages_frame.grid(row=0, column=0, sticky="nsew")
        self._entry_frame.grid(row=1, column=0, sticky="sew", padx=10, pady=15)
        self._entry.grid(row=0, column=1, sticky="nsew", padx=(1, 5), pady=3)
        

    def set_channel(self, channel: Channel | None) -> bool:
        logger.debug(f"Setting channel {channel}, cur: {self._channel}")
        if self._channel == channel:
            return False
        
        if self._loading:
            logger.warning("Already loading text channel")
            return False
        
        self._loading = True
        
        self._channel = channel
        self._scroll_lock = True

        for message in self._message_list:
            message.destroy()
        self._message_list.clear()

        if self._channel is None:
            self._loading = False
            return True
        
        self._messages_frame.configure(label_text=self._channel.name)
        self._entry.configure(placeholder_text=f"Message #{self._channel.name}")
        
        self._messages_frame._parent_canvas.yview_moveto(0)
        #self.update_idletasks()
        self._top_row = START_ROW
        self._bottom_row = START_ROW + 1
        self._scroll_lock = False
        
        def callback():
            messages = self._mm.get_messages(id=0, count=LOAD_COUNT)
            self._load_messages(messages, from_top=False, stick=True)
            # def set_loading_false():
            #     self._loading = False
            # self.after(0, set_loading_false)
            self._loading = False
        self._mm.set_channel(channel, received=callback)
        return True
        
            
                                          
    def _move_scrollbar_after_load(self, message_frame: MessageFrame, top: bool, relative_pos: int | None = None):
        """
        Moves the scrollbar to the bottom, after the given message frame is mapped.
        
        If relative_pos is not None, the scrollbar will be moved to the relative position of the message frame.
        else, the scrollbar will be moved to the bottom.
        
        Relative position is in pixels.
        
        Top indicates whether the relative position was from the top of the viewing area.
        """
        stick = False
        if relative_pos is None:
            relative_pos = 0
            stick = True
            top = False

        #logger.debug("time1")
        self.update_idletasks()
        #logger.debug("time2")
        
        if not top:
            logger.debug(f"parent canvas {self._messages_frame._parent_canvas.winfo_height()}")
            relative_pos -= self._messages_frame._parent_canvas.winfo_height()
        
        logger.debug(f"calculating: {relative_pos}, {message_frame.winfo_y()}, {self._messages_frame.winfo_height()}")
        calculated_pos = (relative_pos + message_frame.winfo_y()) / self._messages_frame.winfo_height()
        
        logger.debug(f"calculated_pos: {calculated_pos}")
        self._messages_frame._parent_canvas.yview_moveto(calculated_pos)
        
        if stick:
            self.update_idletasks()
            self._messages_frame._parent_canvas.yview_moveto(1.0)
        #message_frame.bind("<Map>", lambda e: self._frame_mapped_callback(e, message_frame, relative_pos))

        

    def _load_messages(self, messages: list[Message], from_top: bool = True, stick: bool = False):
        """
        Loads a messages into the frame.
        
        Assumes the messages are sorted in descending order (by id).
        
        Stick = true means the scrollbar will be moved to the bottom after loading the messages.
        """
        if self._channel is None:
            logger.warning("Tried to load messages without setting the channel")
            return
        
        if len(messages) == 0:
            logger.warning("Tried to load 0 messages")
            return
        
        logger.debug(f"loading {len(messages)} messages, from_top: {from_top}, stick: {stick}")
        self._scroll_lock = True

        
        if len(messages) == 1:
            message_frame = MessageFrame(self._messages_frame, message=messages[0], client=self._client)
            if from_top:
                self._message_list.append(message_frame)
            else:
                self._message_list.insert(0, message_frame)
            temp = [message_frame]
        else:
            temp: list[MessageFrame] = [MessageFrame(self._messages_frame, message=message, client=self._client) for message in messages]
            #logger.debug(f"loading\n"+"\n".join([m.message.content for m in temp]))

            
            if from_top:
                self._message_list = self._message_list + temp
            else:
                self._message_list = temp + self._message_list
            
        bottom_message = temp[0]
        if stick:
            self._regrid(temp, from_top, stick=bottom_message)
        else:
            self._regrid(temp, from_top)
        logger.debug(f"y: {bottom_message.winfo_y()}, bottom_message: {bottom_message.message.content}:{bottom_message}")
        logger.debug(f"top_message y: {self._message_list[-1].winfo_y()}")
        
        self._scroll_lock = False
#         logger.debug(f"""Loaded {len(messages)} messages

# {"\n".join([str(m) for m in messages])}

# {"\n".join([str(m.grid_info()) for m in self._message_list])}""")
        

    def _regrid(self, new_message_frames: list[MessageFrame], from_top: bool, stick: MessageFrame | None = None):
        """
        Regrids the message frames.
        
        `from_top` specifies whether the messages are loaded from the top or the bottom.
        """
        # Gigantic wave of off by one error incoming
        # PLEASE don't touch the numbers
        
        total = len(self._message_list)
        count = len(new_message_frames)
        was_empty = total == count
        
        
        logger.debug(f"regridding: {from_top}, {self._top_row}, {self._bottom_row}, count: {count}, total: {total}")
        #logger.debug("\n".join([f"{frame.message.content}:{frame}" for frame in self._message_list]))
        
        if total < MAX_MESSAGES and self._top_row >= MIN_ROW and self._bottom_row <= MAX_ROW:
            if from_top:
                if not was_empty:
                    prev_top_frame = self._message_list[-count - 1]
                    frame_pos = prev_top_frame.winfo_y()
                    rel_pos = (int(self._messages_frame._parent_canvas.yview()[0] * self._messages_frame.winfo_height()) - frame_pos, prev_top_frame)
                for message_frame in new_message_frames:
                    message_frame.grid(row=self._top_row, **MESSAGE_GRID_KWARGS)
                    self._top_row -= 1 # in tkinter higher row = lower position
            else:
                if not was_empty:
                    prev_bottom_frame = self._message_list[count]
                    frame_pos = prev_bottom_frame.winfo_y()
                    rel_pos = (int(self._messages_frame._parent_canvas.yview()[1] * self._messages_frame.winfo_height()) - frame_pos, prev_bottom_frame)
                for message_frame in new_message_frames[::-1]:
                    message_frame.grid(row=self._bottom_row, **MESSAGE_GRID_KWARGS)
                    self._bottom_row += 1
        else:
            self._top_row = START_ROW
            self._bottom_row = START_ROW + MIN_MESSAGES
            


            
            logger.debug(f"scroll region: {self._messages_frame._parent_canvas.bbox('all')}")
            self._messages_frame._parent_canvas.configure(scrollregion=self._messages_frame._parent_canvas.bbox("all"))


            logger.debug(f"regridding2: {from_top}, {self._top_row}, {self._bottom_row}, {total}")
            if from_top:
                if not was_empty:
                    prev_top_frame = self._message_list[-count - 1]
                    frame_pos = prev_top_frame.winfo_y()
                    rel_pos = (int(self._messages_frame._parent_canvas.yview()[0] * self._messages_frame.winfo_height()) - frame_pos, prev_top_frame)
                
                for message_frame in self._message_list.copy()[:-MIN_MESSAGES]:
                    message_frame.destroy()
                    self._message_list.remove(message_frame)
                
                temp_bottom_row = self._bottom_row
                for message_frame in self._message_list:
                    message_frame.grid(row=temp_bottom_row, **MESSAGE_GRID_KWARGS)
                    temp_bottom_row -= 1
                            
                # Band aid solution to force the canvas to update (sorry lol)
                self._messages_frame._parent_canvas.yview_moveto(0)
            else:
                if not was_empty:
                    prev_bottom_frame = self._message_list[count]
                    frame_pos = prev_bottom_frame.winfo_y()
                    rel_pos = (int(self._messages_frame._parent_canvas.yview()[1] * self._messages_frame.winfo_height()) - frame_pos, prev_bottom_frame)
                
                for message_frame in self._message_list.copy()[MIN_MESSAGES:]:
                    message_frame.destroy()
                    self._message_list.remove(message_frame)
                    
                temp_top_row = self._top_row
                for message_frame in self._message_list[::-1]:
                    message_frame.grid(row=temp_top_row, **MESSAGE_GRID_KWARGS)
                    temp_top_row += 1
                    

        
        if stick is not None:
            self._move_scrollbar_after_load(stick, top=False)
        elif not was_empty and rel_pos is not None:
            logger.debug(f"rel_pos: {rel_pos}")
            self._move_scrollbar_after_load(rel_pos[1], from_top, rel_pos[0])
        return
            
    def _scroll_callback(self, event: tk.Event):
        if self._scroll_lock:
            return
        
        yview = self._messages_frame._parent_canvas.yview()
        if yview[0] == 0.0:
            #logger.debug(f"scroll callback {yview}")
            logger.debug(f"loading from top m:{self._message_list[-1].message.content}")
            messages = self._mm.get_messages(id=self._message_list[-1].message.id, before=True, count=LOAD_COUNT)
            #logger.debug(f"loading from top\n"+"\n".join([m.content for m in messages]))
            if len(messages) != 0:
                self._load_messages(messages, from_top=True)
        elif yview[1] == 1.0:
            #logger.debug(f"scroll callback {yview}")
            logger.debug(f"loading from bottom m:{self._message_list[0].message.content}")
            messages = self._mm.get_messages(id=self._message_list[0].message.id, before=False, count=LOAD_COUNT)
            #logger.debug(f"loading from bottom\n"+"\n".join([m.content for m in messages]))
            if len(messages) != 0:
                self._load_messages(messages, from_top=False)
        
    def _send_message(self, event: tk.Event | None = None):
        if self._entry.get() == "":
            return
        if self._channel is None:
            return
        # Temporary message object (need confirmation from server)
        try:
            t = int(datetime.now().timestamp())
            message = Message(t << TAG_BIT_LENGTH, self._channel.id, self._entry.get(), 1, 1, t)
        except ValueError:
            logger.warning("Failed to create message object")
            return
        self._entry.delete(0, 'end')
        self._mm.send_message(message)

        
    def new_message(self, message: Message):
        
        # Add a new message to the frame only if the frame is at (near) the bottom
        if self._messages_frame._parent_canvas.yview()[1] >= 0.95:
            self._load_messages([message], from_top=False, stick=True)
            
            
    def _character_limit(self, d: str, p: str) -> bool:
        """
        Filters entry input
        
        From TK documentation:
        d: Type of action (1=insert, 0=delete, -1 for others)
        p: The text if the edit would be allowed
        """
        if d == "1" and len(p) > MAX_MESSAGE_LENGTH:
            return False
        return True