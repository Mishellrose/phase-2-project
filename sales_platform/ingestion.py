from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, List

from sales_platform.logging_config import get_logger

logger = get_logger(__name__)


class IngestionError(Exception):
    pass


@dataclass(frozen=True)
class IngestionResult:
    records: List[dict[str, Any]]


def load_sales_json(path: str) -> IngestionResult:
    if not os.path.exists(path):                                  #check if file exists
        raise IngestionError(f"Input file does not exist: {path}")

    if os.path.getsize(path) == 0:                              #check if file is empty
        raise IngestionError(f"Input file is empty: {path}")

    try:                                                     #try to read file
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()                                   #store it in raw
    except OSError as e:
        raise IngestionError(f"Failed to read input file: {path} ({e})") from e

    if raw.strip() == "":                                  #if raw is just blank spaces
        raise IngestionError(f"Input file is empty/blank: {path}")

    try:
        data = json.loads(raw)                              #converts string to python object
    except json.JSONDecodeError as e:
        raise IngestionError(f"Invalid JSON in input file: {path} ({e})") from e

    if not isinstance(data, list):                         #check if its a list
        raise IngestionError("Input JSON must be an array of records.")

    records: List[dict[str, Any]] = []                     #create empty 
    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            logger.warning("Skipping non-object record at index %s: %r", idx, item)
            continue
        records.append(item)

    logger.info("File loaded: %s (records=%s)", path, len(records))
    return IngestionResult(records=records)

