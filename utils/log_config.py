import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from platformdirs import user_log_dir

APP_NAME = "cat-relay"
APP_AUTHOR = "N2IW"
LOG_FILENAME = "cat-relay.log"
LOG_DIR = Path(user_log_dir(APP_NAME, APP_AUTHOR))
LOG_FILE_PATH = LOG_DIR / LOG_FILENAME

_MAX_BYTES = 1_000_000
_BACKUP_COUNT = 5

_configured = False


def setup_logging() -> None:
    global _configured
    if _configured:
        return

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root = logging.getLogger()
    root.setLevel(logging.INFO)

    file_handler = RotatingFileHandler(
        LOG_FILE_PATH,
        maxBytes=_MAX_BYTES,
        backupCount=_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    if sys.stdout is not None:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root.addHandler(console_handler)

    _configured = True
