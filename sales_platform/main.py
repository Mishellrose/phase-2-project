from fastapi import FastAPI, HTTPException
from typing import List, Dict

from sales_platform.config import load_config
from sales_platform.db import create_db_engine, create_tables, insert_sales
from sales_platform.ingestion import IngestionError
from sales_platform.processing import DataProcessor
from sales_platform.reporting import aggregate_by_store, write_store_report
from sales_platform.logging_config import configure_logging, get_logger

app = FastAPI()

logger = get_logger(__name__)

# Load config + setup once
cfg = load_config()
configure_logging(log_level=cfg.log_level, log_path=cfg.log_path)

# Create DB engine once
engine = create_db_engine(cfg.db_url)
create_tables(engine)




@app.post("/process")
def process_data() -> Dict:
    """
    Runs full pipeline:
    - Load file
    - Validate + transform
    - Insert into DB
    - Generate report
    """

    processor = DataProcessor(cfg.input_path)

    try:
        valid_records = processor.run()
    except IngestionError as e:
        logger.exception("Ingestion failed")
        raise HTTPException(status_code=400, detail=str(e))

    # Insert into DB (RAW SQL)
    inserted_count = insert_sales(engine, valid_records)

    # Reporting
    store_totals = aggregate_by_store(valid_records)
    write_store_report(store_totals, cfg.output_report_path)

    logger.info("Pipeline complete")

    return {
        "status": "success",
        "inserted_records": inserted_count,
        "rejected_records": len(processor.last_rejected),
        "store_totals": store_totals,
    }


@app.get("/sales/{store_name}")
def get_sales(store_name: str) -> List[Dict]:
    """
    Fetch sales for a specific store
    """
    from sales_platform.db import fetch_sales_by_store

    results = fetch_sales_by_store(engine, store_name)

    return results