from __future__ import annotations

import json
import os
from typing import Any, List, Dict

from sales_platform.logging_config import get_logger

logger = get_logger(__name__)


class IngestionError(Exception):
   
    pass


def load_sales_json(path: str) -> List[Dict[str, Any]]:
  

   
    if not os.path.exists(path):
        raise IngestionError(f"Input file does not exist: {path}")

 
    if os.path.getsize(path) == 0:
        raise IngestionError(f"Input file is empty: {path}")

  
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
    except OSError as e:
        raise IngestionError(f"Failed to read input file: {path} ({e})") from e

  
    if raw.strip() == "":
        raise IngestionError(f"Input file is empty/blank: {path}")


    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise IngestionError(f"Invalid JSON in input file: {path} ({e})") from e

   
    if not isinstance(data, list):
        raise IngestionError("Input JSON must be an array of records.")


    records: List[Dict[str, Any]] = []

    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            logger.warning(
                "Skipping invalid record at index %s: %r", idx, item
            )
            continue

        records.append(item)

    logger.info("File loaded: %s (records=%s)", path, len(records))

    return records