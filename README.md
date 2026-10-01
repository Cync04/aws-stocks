# Financial Market Data Pipeline

An end-to-end data engineering pipeline that ingests real-time and historical stock market data, processes it at scale with PySpark on AWS Glue, stores it in a Delta Lake table for reliable upserts and versioning, and surfaces insights through Tableau.

This project was built to apply production-style data engineering practices — schema validation, data quality checks, and transactional storage — to a real-world financial dataset.

## Project Goals

- Build a pipeline architecture similar to what's used in production financial data systems
- Practice schema design, data validation, and deduplication at the transformation layer
- Implement Delta Lake MERGE logic for safe, idempotent upserts
- Turn cleaned data into an interactive, insight-driven dashboard

## Architecture

```
Alpha Vantage API
       │
       ▼
   AWS S3 (raw)         → raw/{symbol}/{timestamp}.json
       │
       ▼
  AWS Glue (PySpark)     → schema flattening, type casting, null/duplicate handling
       │
       ▼
   Delta Lake Table       → MERGE-based upserts, ACID transactions, time travel
       │
       ▼
   Tableau Dashboard       → published insights
```

## Tech Stack

| Layer | Tool |
|---|---|
| Data source | [Alpha Vantage API](https://www.alphavantage.co/) |
| Storage (raw) | AWS S3 |
| Transformation | AWS Glue (PySpark) |
| Storage (clean/versioned) | Delta Lake |
| Visualization | Tableau Public |
| Local dev | Python, boto3, python-dotenv |

## Status — In Progress

- [x] AWS environment setup (S3 bucket, IAM user/role, boto3 config)
- [x] Ingestion script — pulls daily OHLCV data from Alpha Vantage, lands raw JSON in S3
- [x] Data validation at ingestion — rejects empty/malformed API responses before they reach S3
- [] AWS Glue PySpark transformation job — flattens nested JSON, casts types, drops nulls/duplicates
- [ ] Delta Lake table setup with MERGE logic for upserts
- [ ] Failure handling / retry logic for pipeline runs
- [ ] Tableau dashboard connected to cleaned Delta Lake output
- [ ] Architecture diagram and final documentation pass

## Planned Pipeline Details

**Ingestion (`ingest.py`)**
Pulls daily time series data (OHLCV: open, high, low, close, volume) for selected stock symbols from Alpha Vantage. Raw JSON responses are validated before being written to S3, partitioned by symbol and timestamp, so bad API responses (rate limits, errors) never pollute the raw layer.

**Transformation (AWS Glue / PySpark)**
Reads raw JSON from S3, explodes the nested daily time series into row-level records, casts all fields from string to proper numeric types, and removes null or duplicate trading dates. Outputs cleaned data as Parquet, partitioned by symbol.

**Storage (Delta Lake)**
Cleaned data is loaded into a Delta Lake table using MERGE logic — new records are inserted, existing records with matching primary keys are skipped or updated, preventing duplicate entries on reprocessing. This also enables time travel for rolling back to prior table states if a bad run occurs.

**Visualization (Tableau)**
The final Delta Lake output feeds a Tableau Public dashboard highlighting price trends, volatility, and volume patterns across tracked symbols.

## Data Quality Approach

Following the same validation principles used in production systems, this pipeline includes:
- Pre-ingestion validation to reject rate-limited or malformed API responses
- Type enforcement during transformation (all numeric fields cast from string)
- Null and duplicate handling before data reaches the clean layer
- Idempotent writes via Delta Lake MERGE to prevent duplicate records on reprocessing

## Setup

```bash
pip install requests boto3 python-dotenv
```

Create a `.env` file in the project root:
```
ALPHA_VANTAGE_KEY=your_key_here
AWS_BUCKET=your_bucket_name
```

Run ingestion:
```bash
python scripts/load_data.py
```

## Next Steps

See the Status section above — Delta Lake MERGE logic and the Tableau dashboard are the current focus.

---

*This project is a work in progress, built as hands-on practice for data engineering roles in financial services.*
