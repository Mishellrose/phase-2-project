from __future__ import annotations

import os
from typing import Dict

from sales_platform.logging_config import get_logger

logger = get_logger(__name__)


def _ensure_parent_dir(file_path: str) -> None:
    parent = os.path.dirname(file_path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def write_store_report(store_totals: Dict[str, float], output_path: str) -> None:
    _ensure_parent_dir(output_path)

    lines: list[str] = []
    lines.append("Total Sales Per Store")
    lines.append("=====================")
    lines.append("")

    for store in sorted(store_totals.keys()):
        lines.append(f"{store}: {store_totals[store]:.2f}")

    content = "\n".join(lines) + "\n"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    logger.info("Report saved: %s", output_path)

