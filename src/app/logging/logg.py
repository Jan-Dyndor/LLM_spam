import sys

from loguru import logger


def set_up_logging():
    logger.remove()
    logger.add(
        sys.stdout,
        level="INFO",
        backtrace=True,
        diagnose=False,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "id={extra[request_id]} "
            "- <level>{message}</level>"
        ),
    )
    logger.configure(extra={"request_id": "DEFAULT REQUEST_ID VALUE"})
