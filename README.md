# EY Data Platform

Production-ready data pipeline on GCP for e-commerce analytics with batch and near real-time ingestion.

## Architecture & Design Decisions

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌─────────────┐
│ FakeStore   │    │ Ingestion    │    │ Raw Data    │    │ Analytics   │
│ API         │────│ Pipelines    │────│ (BigQuery)  │────│ Star Schema │
└─────────────┘    └──────────────┘    └─────────────┘    └─────────────┘
                            │
                   ┌────────┼────────┐
                   │                 │
            ┌──────▼──────┐  ┌───────▼───────┐
            │ Batch       │  │ Streaming     │
            │ Products    │  │ Carts         │
            │ Users       │  │ (Pub/Sub)     │
            └─────────────┘  └───────────────┘
```

### Key Design Decisions
- **Cloud-first**: GCP services for scalability and reliability
- **JSONL format**: Efficient BigQuery loading and storage
- **Pub/Sub messaging**: Reliable real-time data streaming  
- **dbt transformations**: Maintainable SQL-based transforms
- **Pydantic validation**: Strong data typing and validation

## Project Status

### ✅ Completed Components
- **Batch Pipeline**: Products & Users ingestion (GCS → BigQuery) with idempotent daily processing
- **Streaming Pipeline**: Carts API polling → Pub/Sub → BigQuery with event metadata and deduplication
- **Raw Data Storage**: Immutable JSONL files in GCS with date-based partitioning
- **BigQuery Infrastructure**: Raw datasets with proper partitioning and clustering
- **Event Architecture**: UUID-based event IDs, extraction/publish timestamps, and cart analytics focus

### 🎯 Next Steps
- **dbt Transformations**: Create star schema from raw data
- **Analytics Models**: Transform raw cart events, products, and users into dimensional model
- **Documentation**: Complete architecture diagram and deployment guide

## Quick Verification

The pipeline is working end-to-end. To verify:

```bash
# Check raw data in BigQuery
bq query "SELECT COUNT(*) as products FROM ey-data-platform.bq_raw.Products"
bq query "SELECT COUNT(*) as users FROM ey-data-platform.bq_raw.Users" 
bq query "SELECT COUNT(*) as cart_events FROM ey-data-platform.bq_raw.carts_events"
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

*Coming Soon - dbt transformations for star schema*

```bash
cd dbt/
dbt run    # Transform raw data to analytics tables  
dbt test   # Run data quality tests
```

## Assumptions & Limitations

### Assumptions
- FakeStore API availability and rate limits
- GCP resources provisioned and accessible
- Static API data (same 20 products, 10 users, 7 carts)
- JSONL format acceptable for all data loads

### Current Limitations  
- **No incremental processing**: Full reload on each batch run
- **dbt transformations**: Not yet implemented
- **Streaming BigQuery load**: Currently saves to GCS only
- **Error handling**: Basic error logging, no dead letter queues
- **Monitoring**: No alerting or dashboards configured
- **Authentication**: Service account key file (not recommended for production)

### Production Readiness TODOs
- [ ] Implement dbt star schema transformations
- [ ] Add streaming BigQuery loading 
- [ ] Implement proper secret management
- [ ] Add monitoring and alerting
- [ ] Set up CI/CD pipeline
- [ ] Add data quality tests and validation