from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, List

from sales_platform.ingestion import load_sales_json
from sales_platform.logging_config import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class RejectedRecord:
    record: dict[str, Any]
    reason: str


class DataProcessor:
    def __init__(self, input_file_path: str):
        self.input_file_path = input_file_path
        self.last_rejected: List[RejectedRecord] = []

    def _reject(self, record: dict[str, Any], reason: str) -> RejectedRecord:
        logger.warning("Rejected record (%s): %r", reason, record)
        return RejectedRecord(record=record, reason=reason)

    def _parse_price(self, value: Any) -> Decimal:
        if value is None:
            raise ValueError("price is null")
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError) as e:
            raise ValueError(f"price is not a number: {value!r}") from e

    def _parse_qty(self, value: Any) -> int:
        if value is None:
            raise ValueError("qty is null")
        if isinstance(value, bool):
            raise ValueError("qty must be an integer, not boolean")
        try:
            return int(value)
        except (TypeError, ValueError) as e:
            raise ValueError(f"qty is not an integer: {value!r}") from e

    def validate_and_transform(self, records: List[dict[str, Any]]) -> List[dict[str, Any]]:
        valid: List[dict[str, Any]] = []
        rejected: List[RejectedRecord] = []

        for record in records:
            if "price" not in record:
                rejected.append(self._reject(record, "missing price"))
                continue
            if "qty" not in record:
                rejected.append(self._reject(record, "missing qty"))
                continue

            try:
                price = self._parse_price(record.get("price"))
                qty = self._parse_qty(record.get("qty"))
            except ValueError as e:
                rejected.append(self._reject(record, str(e)))
                continue

            total_sale = price * Decimal(qty)

            transformed = {
                "store": str(record.get("store")),
                "product": str(record.get("product")),
                "price": float(price),
                "quantity": qty,
                "total_sale": float(total_sale),
            }

            valid.append(transformed)

        self.last_rejected = rejected

        logger.info(
            "Records processed: valid=%s rejected=%s",
            len(valid),
            len(rejected),
        )

        return valid

    def run(self) -> List[dict[str, Any]]:
        # Step 1: Load data
        records = load_sales_json(self.input_file_path)

        # Step 2: Validate + transform
        valid_records = self.validate_and_transform(records)

        # ONLY return valid records (as per senior requirement)
        return valid_records