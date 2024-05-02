from PIL import Image
import os
from os.path import dirname

# Lytecord root directory
DIR = os.path.join(dirname(dirname(dirname(dirname(os.path.realpath(__file__))))), "assets")

LIGHT_MODE_ICON = "#252525"
DARK_MODE_ICON = "#dcdcdc"

# ============Icons============
# Attachment button icon
ATTACHMENT_ICON_LIGHT = Image.open(os.path.join(DIR, "icons/attach64light.png"))
ATTACHMENT_ICON_DARK = Image.open(os.path.join(DIR, "icons/attach64dark.png"))

# Default guild icon
GUILD_ICON_LIGHT = Image.open(os.path.join(DIR, "icons/guild256light.png"))
GUILD_ICON_DARK = Image.open(os.path.join(DIR, "icons/guild256dark.png"))

# Attached image error icon
IMG_ERR_ICON_LIGHT = Image.open(os.path.join(DIR, "icons/warning512light.png"))
IMG_ERR_ICON_DARK = Image.open(os.path.join(DIR, "icons/warning512dark.png"))

# Placeholder image attachment icon
IMG_ICON_LIGHT = Image.open(os.path.join(DIR, "icons/image512light.png"))
IMG_ICON_DARK = Image.open(os.path.join(DIR, "icons/image512dark.png"))

# Join guild button icon
JOIN_GUILD_ICON_LIGHT = Image.open(os.path.join(DIR, "icons/join_guild512light.png"))
JOIN_GUILD_ICON_DARK = Image.open(os.path.join(DIR, "icons/join_guild512dark.png"))

# Create guild button icon
CREATE_GUILD_ICON_LIGHT = Image.open(os.path.join(DIR, "icons/create_guild512light.png"))
CREATE_GUILD_ICON_DARK = Image.open(os.path.join(DIR, "icons/create_guild512dark.png"))