from io import BytesIO
import time
from typing import Callable
import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkFont, CTkTextbox, CTkProgressBar, CTkImage
import tkinter as tk
from datetime import datetime
from loguru import logger
from PIL import Image, ImageDraw
from PIL.Image import Image as ImageType

from src.client.client import Client
from src.client.ui.design import IMG_ERR_ICON_LIGHT, IMG_ERR_ICON_DARK, IMG_ICON_LIGHT, IMG_ICON_DARK
from src.shared.attachment import Attachment

MAX_WIDTH = 2**10
MAX_HEIGHT = 2**9

class LoadableImage(CTkFrame):
    def __init__(self, *args, image: ImageType | Attachment, corner_radius: int, client: Client, max_width: int, max_height: int, **kwargs):
        if isinstance(image, Attachment):
            width = image.width
            height = image.height
        else:
            width, height = image.size
            
        if width > max_width:
            ratio = height / width
            width = max_width
            height = round(width * ratio)
        if height > max_height:
            ratio = width / height
            height = max_height
            width = round(height * ratio)
                
        
        logger.debug(f"Image size: {width}x{height}")
        super().__init__(*args, corner_radius=corner_radius, **kwargs)
        self.client = client
        self._loading = False
        self._image = image
        self._corner_radius = corner_radius
        self.width = width
        self.height = height
        
        if isinstance(self._image, ImageType):
            self._image = self._image.convert("RGBA")
        
        self._image_label = CTkLabel(self, text="", fg_color="transparent", corner_radius=0)
        self._image_label.grid(row=1, column=1, sticky="nsew", padx=0, pady=0)
        self._image_label.grid_remove()
        
        scaling = self._image_label._get_widget_scaling()
        self.width_scaled, self.height_scaled = round(width * scaling), round(height * scaling)
        self.radius_scaled = round(self._corner_radius * scaling)
        logger.debug(f"width: {self.width_scaled}, height: {self.height_scaled}, scaling: {scaling}")
        
        self.grid_columnconfigure((0, 2), weight=1, minsize=10)
        self.grid_columnconfigure(1, minsize=self.width_scaled)
        self.grid_rowconfigure((0, 2), weight=1, minsize=10)
        self.grid_rowconfigure(1, minsize=self.height_scaled)
        
        self._loading_animation = CTkProgressBar(self, mode="indeterminate")
        self._loading_animation.grid(row=1, column=0, columnspan=3, sticky="ew", padx=20, pady=10)
        self._loading_animation.grid_remove()
        
        self.configure(width=self.width_scaled, height=self.height_scaled)
        
    
    def _display_image(self):
        if isinstance(self._image, Attachment):
            logger.warning("Load image first")
            return
        
        
        self._image = self.add_corners(self._image, self.radius_scaled)
        logger.debug(f"width scaled: {self.width_scaled}, height scaled: {self.height_scaled}, radius: {self._corner_radius}")
        logger.debug(f"size: {self._image.size}, format: {self._image.format}, mode: {self._image.mode}, pallette: {self._image.palette}, info: {self._image.info}, bands: {self._image.getbands()}")
        self._image = self._image.convert("RGBA")
        image = CTkImage(light_image=self._image, size=(self.width, self.height))
        self.configure(corner_radius=0, fg_color="transparent")
        self._image_label.configure(image=image)
        self._image_label.grid()
        logger.info("Image loaded")
        self._loading = False
        
    def _failed_to_load(self, message: str):
        logger.error(message)
        error_image = CTkImage(light_image=IMG_ERR_ICON_LIGHT, dark_image=IMG_ERR_ICON_DARK, size=(150, 150))
        self._image_label.configure(image=error_image)
        self._image_label.grid()
    
    def load(self, event_loop_insert: Callable | None = None, delay: int = 0):
        if self._loading:
            return
        self._loading = True
        
        if isinstance(self._image, ImageType):
            if event_loop_insert:
                event_loop_insert(delay, self._display_image)
            else:
                self._display_image()
            return
        
        def callback(image_file: bytes | None, message: str):
            self._loading = False
            if not self.winfo_exists():
                return
            self._loading_animation.stop()
            self._loading_animation.grid_remove()
            
            if image_file is None:
                self._failed_to_load(f'Failed to load image: {message}')
                return
            
            try:
                image = Image.open(BytesIO(image_file)).convert("RGBA")
            except Exception as e:
                logger.exception("Failed to open image")
                self._failed_to_load("Failed to open image")
                return
                
            self._image = image
            self._display_image()
                
        self._loading_animation.start()
        self._loading_animation.grid()
        
        if event_loop_insert:
            event_loop_insert(delay, self.client.get_attachment_file, self._image.id, callback)
        else:
            self.client.get_attachment_file(self._image.id, callback)

    
    @staticmethod
    def add_corners(im: ImageType, rad: int):
        circle = Image.new('L', (rad * 2, rad * 2), 0)
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0, rad * 2 - 1, rad * 2 - 1), fill=255)
        alpha = Image.new('L', im.size, 255)
        w, h = im.size
        alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
        alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
        alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
        alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
        im.putalpha(alpha)
        return im