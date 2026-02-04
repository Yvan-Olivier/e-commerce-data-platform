# EY Data Platform

Production-ready data pipeline on GCP for e-commerce analytics with batch and near real-time ingestion.

## Architecture & Design Decisions

**📋 Complete Technical Documentation**: [docs/architecture.md](docs/architecture.md)

**🎨 Professional Architecture Diagram**: [docs/architecture.mmd](docs/architecture.mmd)

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────┐    ┌─────────────┐
│ FakeStore   │    │ Ingestion    │    │ Raw Data    │    │   dbt    │    │ Analytics   │
│ API         │────│ Pipelines    │────│ (BigQuery)  │────│Transform.│────│ Star Schema │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────┘    └─────────────┘
                            │                                     │
                   ┌────────┼────────┐                   ┌────────┼────────┐
                   │                 │                   │                 │
            ┌──────▼──────┐  ┌───────▼───────┐    ┌─────▼─────┐  ┌────────▼────────┐
            │ Batch       │  │ Streaming     │    │ Staging   │  │ Marts           │
            │ Products    │  │ Carts         │    │ (Views)   │  │ (Tables)        │
            │ Users       │  │ (Pub/Sub)     │    │ Clean     │  │ dim_users       │
            └─────────────┘  └───────────────┘    │ Raw Data  │  │ dim_products    │
                                                   └───────────┘  │ fact_orders     │
                                                                  └─────────────────┘
```

### Key Design Decisions
- **Cloud-first**: GCP services for scalability and reliability
- **JSONL format**: Efficient BigQuery loading and storage
- **Pub/Sub messaging**: Reliable real-time data streaming  
- **dbt transformations**: Maintainable SQL-based transforms
- **Pydantic validation**: Strong data typing and validation

## Project Status

### ✅ Production-Ready Data Platform
- **Complete End-to-End Pipeline**: APIs → Raw Data → Analytics Star Schema
- **Batch Ingestion**: Products & Users with idempotent daily processing
- **Streaming Ingestion**: Real-time cart events via Pub/Sub with deduplication
- **Data Transformations**: dbt star schema with staging and marts layers
- **Analytics Tables**: dim_users, dim_products, fact_orders optimized for BI tools
- **Quality Assurance**: Validated data flow with 31 total records processed

## Quick Verification

The complete pipeline is operational. To verify:

### Raw Data (BigQuery bq_raw dataset)
```bash
bq query "SELECT COUNT(*) as products FROM ey-data-platform.bq_raw.Products"     # Expected: 20
bq query "SELECT COUNT(*) as users FROM ey-data-platform.bq_raw.Users"           # Expected: 10  
bq query "SELECT COUNT(*) as cart_events FROM ey-data-platform.bq_raw.carts_events" # Expected: 1+
```

### Analytics Tables (BigQuery bq_analytics dataset)
```bash
bq query "SELECT COUNT(*) FROM ey-data-platform.bq_analytics.dim_products"       # Expected: 20
bq query "SELECT COUNT(*) FROM ey-data-platform.bq_analytics.dim_users"          # Expected: 10
bq query "SELECT COUNT(*) FROM ey-data-platform.bq_analytics.fact_orders"        # Expected: 1+
```

### End-to-End Test
```bash
python test_end_to_end.py  # Validates complete data flow API → Analytics
```

### Prerequisites
1. GCP Project with billing enabled
2. Service Account with permissions:
   - BigQuery Admin
   - Storage Admin  
   - Pub/Sub Admin
3. Environment configuration (`.env` file)

### GCP Resources Required
```bash
# BigQuery datasets
bq_raw              # Raw ingested data
bq_analytics        # Transformed analytics tables

# Cloud Storage  
{project}-raw-data  # JSONL files storage

# Pub/Sub
carts-events        # Topic for cart events
carts-events-sub    # Subscription for processing
```

## How to Run Batch Ingestion

```bash
# Run batch pipeline for products and users
python -m ingestion.batch.batch_ingest

# Verify data loaded to BigQuery
python test_bigquery.py
```

**Output**: 
- Products: 20 records in `bq_raw.Products`
- Users: 10 records in `bq_raw.Users`

## How Near Real-Time Ingestion Works

### Architecture
```
FakeStore Carts API → API Poller → Pub/Sub → Consumer → GCS → BigQuery
                     (60s poll)            (buffered)
```

### Running the Pipeline

1. **Start API Poller** (polls carts API every 60 seconds)
```bash
python -m ingestion.streaming.carts_poller
```

2. **Start Consumer** (processes Pub/Sub messages)
```bash  
python -m ingestion.streaming.carts_consumer
```

3. **Test End-to-End**
```bash
python test_end_to_end.py
```

**Data Flow**:
- Polls 7 carts from API every 60 seconds
- Publishes cart events to Pub/Sub topic
- Consumer saves events to GCS in JSONL format
- Ready for BigQuery loading

## How to Run dbt

### Prerequisites
1. Ensure your virtual environment is activated
2. Raw data exists in BigQuery (run ingestion pipelines first)
3. dbt profiles configured for BigQuery connection

### Setup dbt Profile (one-time)
```bash
# Create dbt profile directory
mkdir -p ~/.dbt

# Profile automatically created at ~/.dbt/profiles.yml
# Points to BigQuery bq_analytics dataset
```

### Transform Raw Data to Star Schema
```bash
# Activate virtual environment
source .venv/bin/activate

# Test dbt connection
dbt debug

# Run all transformations (staging → marts)
dbt run

# Generate documentation
dbt docs generate
```

### Verify Results
```bash
# List created models
dbt ls

# Check model lineage
dbt run-operation list_models
```

**Output**: Creates 6 models in BigQuery bq_analytics dataset:
- **Staging Views**: stg_products, stg_users, stg_cart_events
- **Dimension Tables**: dim_products (20 rows), dim_users (10 rows)
- **Fact Table**: fact_orders (partitioned by date, 1+ rows from streaming)

## Assumptions & Limitations

### Design Assumptions
- **FakeStore API**: Reliable public API with consistent data structure
- **GCP Infrastructure**: Provisioned BigQuery, GCS, Pub/Sub resources
- **Data Freshness**: Daily batch updates acceptable for products/users
- **Event Volume**: Cart polling suitable for demo-scale traffic
- **Data Format**: JSONL optimal for BigQuery loading

### Current Implementation
- **Full Refresh**: Batch pipeline reloads all data daily (idempotent)
- **Streaming Pattern**: API polling simulates real-time events
- **Analytics Focus**: Star schema optimized for BI and reporting
- **Development Auth**: Service account key file (production should use Workload Identity)

### Production Enhancements
For enterprise deployment, consider:
- **Incremental Processing**: CDC or timestamp-based incremental loads
- **True Streaming**: Replace API polling with webhooks/Kafka
- **Monitoring**: Add DataDog/GCP Monitoring for pipeline health
- **Data Quality**: Implement Great Expectations or similar framework
- **CI/CD**: Automated testing and deployment pipelines
- **Secret Management**: Google Secret Manager integration