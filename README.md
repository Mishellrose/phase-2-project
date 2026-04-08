# Setup

Create a virtual environment (recommended) and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

# How to run

Run the pipeline:

```bash
python -m sales_platform.main
```

On systems where `python` is not available but `python3` is:

```bash
python3 -m sales_platform.main
```

After a successful run, you should see:

- `sales.db` (SQLite database) with a populated `sales` table
- `output/report.txt` (plain text report)
- `output/app.log` (log file for the run)

# Sample Data
 You can find sample data array in /Data directory

# Assumptions

- Input is a JSON **array** of objects, each containing:
  - `store` (string)
  - `product` (string)
  - `price` (number or null)
  - `qty` (integer or null)
- Any record with missing or null `price` or `qty` is rejected and logged with a reason.
- Database is SQLite by default, but can be swapped to another SQLAlchemy-supported database by changing `SALES_DB_URL` (no code changes required).

