import re
from sys import stderr

import loguru
from loguru import logger

FORMAT = "<green>[{time:YYYY-MM-DD  HH:mm:ss.SSS}]</green>  <level>---{level}---</level>  <cyan>[{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}]</cyan>\n<level>{extra[obfuscated_message]}\n{exception}</level>"

PASSWORD_REGEX = r"(?P<pre>password: |password:|(?P<json>[\"']password[\"']:[\"']))(?P<pw>[^\s,]+)(?P<post>(?(json)['\"]))"
SUB = r"\g<pre>****\g<post>"

def obfuscate_message(message: str):
    """Obfuscate sensitive information."""
    result = re.sub(PASSWORD_REGEX, SUB, message, flags=re.IGNORECASE)
    return result

def formatter(record):
    record["extra"]["obfuscated_message"] = obfuscate_message(record["message"])
    return FORMAT

logger.remove()
logger.add(stderr, format=formatter)
logger.info("Loguru configured successfully")