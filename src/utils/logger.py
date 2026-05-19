"""
Logging Configuration

Sets up structured logging using loguru with file and console output.
"""

import sys
from pathlib import Path
from loguru import logger
from .config import Config


def setup_logger(config: Config) -> None:
    """
    Configure application logging.

    Args:
        config: Configuration object with logging settings
    """
    # Remove default logger
    logger.remove()

    # Console logging
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=config.LOG_LEVEL,
        colorize=config.COLORIZE_OUTPUT,
    )

    # File logging
    log_file = Path(config.LOG_FILE)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    if config.LOG_FORMAT == "json":
        logger.add(
            log_file,
            format="{time} {level} {message}",
            level=config.LOG_LEVEL,
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            serialize=True,  # JSON format
        )
    else:
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=config.LOG_LEVEL,
            rotation="10 MB",
            retention="30 days",
            compression="zip",
        )

    logger.info(
        f"Logger initialized with level {config.LOG_LEVEL}, output to {log_file}"
    )


def get_logger(name: str):
    """
    Get a logger instance for a specific module.

    Args:
        name: Module name (typically __name__)

    Returns:
        Logger instance
    """
    return logger.bind(module=name)
