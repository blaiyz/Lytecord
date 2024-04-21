from sys import stderr
import loguru
from loguru import logger

FORMAT = "<green>[{time:YYYY-MM-DD  HH:mm:ss.SSS}]</green>  <level>[{level}]</level>  <cyan>[{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}]</cyan>\n<level>{message}</level>"


logger.remove()
logger.add(stderr, format=FORMAT)
logger.info("Loguru configured successfully")