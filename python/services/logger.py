import logging
import os
from datetime import datetime


def _create_log_dir() -> str:
    now = datetime.now()

    year = now.strftime("%Y")
    month = now.strftime("%m")

    log_dir = os.path.join("logs", year, month)

    os.makedirs(log_dir, exist_ok=True)

    return log_dir


def _create_logger() -> logging.Logger:
    log_dir = _create_log_dir()

    log_filename = datetime.now().strftime("%Y%m%d_%H%M%S.log")
    log_path = os.path.join(log_dir, log_filename)

    logger = logging.getLogger("youtube_rss")

    # 二重登録防止
    if logger.handlers:
        return logger

    logger.setLevel(logging.ERROR)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s"
    )

    file_handler = logging.FileHandler(
        log_path,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger


logger = _create_logger()