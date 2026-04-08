from __future__ import annotations

import os
from dataclasses import dataclass


def _env(name: str, default: str) -> str:
    value = os.getenv(name)
    return default if value is None or value.strip() == "" else value.strip()


@dataclass(frozen=True)
class Config:
    input_path: str
    output_report_path: str
    log_path: str
    db_url: str
    log_level: str


def load_config() -> Config:
    return Config(
        input_path=_env("SALES_INPUT_PATH", "data/sample_sales.json"),
        output_report_path=_env("SALES_OUTPUT_REPORT_PATH", "output/report.txt"),
        log_path=_env("SALES_LOG_PATH", "output/app.log"),
        db_url=_env("SALES_DB_URL", "sqlite:///sales.db"),
        log_level=_env("SALES_LOG_LEVEL", "INFO").upper(),
    )

