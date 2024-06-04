import os
from os.path import dirname

from PIL import Image

# Lytecord root directory
DIR = os.path.join(dirname(dirname(dirname(dirname(os.path.realpath(__file__))))), "assets")

def join(*args):
    return os.path.join(DIR, *args)

def open_img(*args):
    return Image.open(join(*args))


LIGHT_MODE_ICON = "#252525"
DARK_MODE_ICON = "#dcdcdc"

# ============Icons============
# Attachment button icon
ATTACHMENT_ICON_LIGHT = open_img("icons/attach64light.png")
ATTACHMENT_ICON_DARK = open_img("icons/attach64dark.png")

# Default guild icon
GUILD_ICON_LIGHT = open_img("icons/guild256light.png")
GUILD_ICON_DARK = open_img("icons/guild256dark.png")

# Attached image error icon
IMG_ERR_ICON_LIGHT = open_img("icons/warning512light.png")
IMG_ERR_ICON_DARK = open_img("icons/warning512dark.png")

# Placeholder image attachment icon
IMG_ICON_LIGHT = open_img("icons/image512light.png")
IMG_ICON_DARK = open_img("icons/image512dark.png")

# Join guild button icon
JOIN_GUILD_ICON_LIGHT = open_img("icons/join_guild512light.png")
JOIN_GUILD_ICON_DARK = open_img("icons/join_guild512dark.png")

# Create guild button icon
CREATE_GUILD_ICON_LIGHT = open_img("icons/create_guild512light.png")
CREATE_GUILD_ICON_DARK = open_img("icons/create_guild512dark.png")

# Refresh code
REFRESH_ICON_LIGHT = open_img("icons/refresh128light.png")
REFRESH_ICON_DARK = open_img("icons/refresh128dark.png")

# Download button
DOWNLOAD_ICON_LIGHT = open_img("icons/download128light.png")
DOWNLOAD_ICON_DARK = open_img("icons/download128dark.png")

# Hashtag
HASHTAG_ICON_LIGHT = open_img("icons/hashtag128light.png")
HASHTAG_ICON_DARK = open_img("icons/hashtag128dark.png")
