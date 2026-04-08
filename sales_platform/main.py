from __future__ import annotations

from sales_platform.config import load_config
from sales_platform.db import (
    create_db_engine,
    create_session_factory,
    create_tables,
    insert_sales,
    to_sale_models,
)
from sales_platform.ingestion import IngestionError
from sales_platform.logging_config import configure_logging, get_logger
from sales_platform.processing import DataProcessor
from sales_platform.reporting import write_store_report

logger = get_logger(__name__)


def run_pipeline() -> None:
    cfg = load_config()
    configure_logging(log_level=cfg.log_level, log_path=cfg.log_path)

    logger.info("Starting pipeline")

    processor = DataProcessor(cfg.input_path)
    try:
        valid_records = processor.run()
    except IngestionError:
        logger.exception("Ingestion failed")
        raise

    rejected = processor.last_rejected

    for rej in rejected:
        logger.debug("Rejected record detail: reason=%s record=%r", rej.reason, rej.record)

    store_totals = processor.aggregate_by_store(valid_records)
    processor.aggregate_by_product(valid_records)

    engine = create_db_engine(cfg.db_url)
    create_tables(engine)

    SessionLocal = create_session_factory(engine)
    with SessionLocal() as session:
        sale_models = to_sale_models(valid_records)
        insert_sales(session, sale_models)

    write_store_report(store_totals, cfg.output_report_path)

    logger.info("Pipeline complete")


if __name__ == "__main__":
    run_pipeline()

