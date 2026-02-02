# EY Data Platform

A data ingestion system for e-commerce data with batch and streaming pipelines.

## Architecture Overview

```
FakeStore API → GCS (Raw Data) → BigQuery (Data Warehouse)
```

## What's Implemented

### ✅ Batch Ingestion Pipeline
- **Source**: FakeStore API (products, users)
- **Storage**: Google Cloud Storage (JSONL format)
- **Warehouse**: BigQuery tables
- **Schedule**: On-demand (ready for scheduling)

### ✅ Data Validation
- Pydantic models for data validation
- Automatic schema enforcement
- Error handling and logging

### ✅ Configuration Management
- Environment-based configuration
- Secure credential handling
- Project settings centralized

## Project Structure

```
├── ingestion/
│   ├── batch/          # Batch processing
│   │   └── batch_ingest.py
│   ├── streaming/      # Streaming (planned)
│   └── common/         # Shared utilities
│       ├── api_client.py
│       ├── config.py
│       └── models.py
├── dbt/                # Data transformation
├── .env.example        # Configuration template
└── README.md
```

## Quick Start

1. **Setup Environment**
   ```bash
   cp .env.example .env
   # Update .env with your GCP credentials
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt  # From pyproject.toml
   ```

3. **Run Batch Ingestion**
   ```bash
   python test_batch_ingest.py
   ```

4. **Verify Data**
   ```bash
   python test_bigquery.py
   ```

## Current Data Flow

1. **Extract**: Fetch data from FakeStore API
2. **Transform**: Validate with Pydantic models
3. **Load**: Save to GCS as JSONL files
4. **Warehouse**: Load to BigQuery tables

## BigQuery Tables Created

- `bq_raw.Products` (20 products)
- `bq_raw.Users` (10 users)

## Next Steps

- [ ] Streaming ingestion (carts, orders)
- [ ] Pub/Sub integration
- [ ] Data transformation with dbt
- [ ] Monitoring and alerting

## Tech Stack

- **Language**: Python 3.13
- **Cloud**: Google Cloud Platform
- **Storage**: Google Cloud Storage
- **Warehouse**: BigQuery
- **Validation**: Pydantic
- **Environment**: Virtual environment (.venv)