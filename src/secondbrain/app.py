import os
import sys
from pathlib import Path

from loguru import logger


def configure_logging():
    """Configure loguru for console and file logging.

    The stderr handler uses LOG_LEVEL, which defaults to INFO. The DEBUG file
    handler uses LOG_FILE when set. Otherwise it writes to
    ~/.secondbrain/logs/app.log and creates the parent directory if needed.
    """
    log_level = os.environ.get("LOG_LEVEL", "INFO")
    log_file: str | Path | None = os.environ.get("LOG_FILE")
    if log_file is None:
        log_file = Path.home() / ".secondbrain" / "logs" / "app.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)

    logger.remove()
    logger.add(
        sys.stderr,
        level=log_level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level.name:.3}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
    )
    logger.add(log_file, level="DEBUG", rotation="50 KB", retention=1)


@logger.catch
def main():
    """Run the application.

    Configures logging and prints a greeting to verify the setup works.
    """
    configure_logging()
    logger.info("Hello from secondbrain!")
