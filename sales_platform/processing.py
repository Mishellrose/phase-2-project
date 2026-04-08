from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Tuple

from sales_platform.ingestion import IngestionError, load_sales_json
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
            qty = int(value)
        except (TypeError, ValueError) as e:
            raise ValueError(f"qty is not an integer: {value!r}") from e
        return qty

    def validate_and_transform(
        self, records: List[dict[str, Any]]
    ) -> Tuple[List[dict[str, Any]], List[RejectedRecord]]:
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
            transformed = dict(record)
            transformed["price"] = float(price)
            transformed["qty"] = qty
            transformed["total_sale"] = float(total_sale)
            valid.append(transformed)

        logger.info(
            "Records processed: valid=%s rejected=%s", len(valid), len(rejected)
        )
        return valid, rejected

    def unique_stores(self, valid_records: List[dict[str, Any]]) -> List[str]:
        stores = {str(r.get("store")) for r in valid_records if r.get("store") is not None}
        result = sorted(stores)
        logger.info("Unique stores extracted: %s", len(result))
        return result

    def aggregate_by_store(self, valid_records: List[dict[str, Any]]) -> Dict[str, float]:
        totals: Dict[str, float] = {}
        for r in valid_records:
            store = str(r.get("store"))
            totals[store] = totals.get(store, 0.0) + float(r.get("total_sale", 0.0))
        return totals

    def aggregate_by_product(self, valid_records: List[dict[str, Any]]) -> Dict[str, float]:
        totals: Dict[str, float] = {}
        for r in valid_records:
            product = str(r.get("product"))
            totals[product] = totals.get(product, 0.0) + float(r.get("total_sale", 0.0))
        return totals

    def run(self) -> List[dict[str, Any]]:
        ingestion = load_sales_json(self.input_file_path)
        valid, rejected = self.validate_and_transform(ingestion.records)
        self.last_rejected = rejected
        self.unique_stores(valid)
        self.aggregate_by_store(valid)
        self.aggregate_by_product(valid)
        return valid

