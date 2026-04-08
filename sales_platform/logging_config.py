from __future__ import annotations

import logging
import os
from typing import Optional


def _ensure_parent_dir(file_path: str) -> None:
    parent = os.path.dirname(file_path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def configure_logging(*, log_level: str, log_path: str) -> None:
    _ensure_parent_dir(log_path)

    root = logging.getLogger()
    root.setLevel(getattr(logging, log_level, logging.INFO))

    for handler in list(root.handlers):
        root.removeHandler(handler)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(root.level)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(root.level)
    file_handler.setFormatter(formatter)

    root.addHandler(console_handler)
    root.addHandler(file_handler)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    return logging.getLogger(name if name else "sales_platform")

