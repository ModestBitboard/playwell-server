import logging
import os

def init_logger():
    log_level = os.getenv("LOG_LEVEL", 'INFO').upper()

    uvicorn_error_logger = logging.getLogger("uvicorn")
    playwell_logger = logging.getLogger("playwell")

    playwell_logger.handlers = uvicorn_error_logger.handlers

    playwell_logger.setLevel(log_level)
    playwell_logger.propagate = False  # Prevent log duplication
    playwell_logger.info(f"Playwell log level set to: {log_level}")
