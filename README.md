# EY Data Platform

Production-ready data pipeline on GCP for e-commerce analytics with batch and near real-time ingestion.

## Architecture & Design Decisions

This data platform implements a cloud-native architecture. The system follows a medallion architecture pattern with clear separation between raw data ingestion, transformation, and analytics consumption.

**System Overview**: [docs/diagram.mmd](docs/diagram.mmd)

**Architecture Diagram**: [docs/architecture.mmd](docs/architecture.mmd)

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────┐    ┌─────────────┐
│ FakeStore   │    │ Ingestion    │    │ Raw Data    │    │   dbt    │    │ Analytics   │
│ API         │────│ Pipelines    │────│ (BigQuery)  │────│Transform │────│ Star Schema │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────┘    └─────────────┘
                            │                                     │
                   ┌────────┼────────┐                   ┌────────┼────────┐
                   │                 │                   │                 │
            ┌──────▼──────┐  ┌───────▼───────┐     ┌─────▼─────┐  ┌────────▼────────┐
            │ Batch       │  │ Streaming     │     │ Staging   │  │ Marts           │
            │ Products    │  │ Carts         │     │ (Views)   │  │ (Tables)        │
            │ Users       │  │ (Pub/Sub)     │     │ Clean     │  │ dim_users       │
            └─────────────┘  └───────────────┘     │ Raw Data  │  │ dim_products    │
                                                   └───────────┘  │ fact_orders     │
                                                                  └─────────────────┘
```

### Key Design Decisions

The platform leverages Google Cloud Platform services to handle different data ingestion patterns. For batch processing, we use Cloud Storage as an immutable data lake to store raw API responses in JSONL format, providing efficient compression and direct BigQuery loading capabilities. For near real-time processing, we implement an event-driven architecture using Pub/Sub to decouple data producers from consumers, ensuring reliable message delivery and processing guarantees.

- **Cloud-first**: GCP services for scalability and reliability
- **JSONL format**: Efficient BigQuery loading and storage
- **Pub/Sub messaging**: Reliable real-time data streaming  
- **dbt transformations**: Maintainable SQL-based transforms
- **Pydantic validation**: Strong data typing and validation

## Infrastructure Deployment

The platform requires several GCP resources to be provisioned before running the data pipelines. Start by creating a GCP project and establishing proper access credentials through a service account with the required IAM roles listed below.

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

## How Batch Ingestion Works

The batch ingestion system processes products and users data from the FakeStore API on a daily schedule, implementing an idempotent design that safely handles reprocessing scenarios.

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌─────────────┐
│ FakeStore   │    │ API Client   │    │ Validation  │    │   Storage   │
│ Products    │───▶│ (Pydantic)   │───▶│ & Transform │───▶│ GCS + BQ    │
│ Users APIs  │    │ HTTP Requests│    │    JSONL    │    │  Raw Data   │
└─────────────┘    └──────────────┘    └─────────────┘    └─────────────┘
                                              │
                                    ┌─────────▼──────────┐
                                    │ Date-partitioned   │
                                    │ products_YYYY-MM-DD│
                                    │ users_YYYY-MM-DD   │
                                    └────────────────────┘
```

The system operates with idempotent design ensuring that rerunning the pipeline for the same date will not create duplicate data or corrupt existing records. Each run processes current product and user data from the API, storing them as immutable JSONL files in Cloud Storage before loading into BigQuery raw tables.

## How Near Real-Time Ingestion Works

The streaming ingestion system simulates real-time processing by continuously polling the FakeStore carts API and publishing cart events through a Pub/Sub messaging pattern.

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ FakeStore   │    │ API Poller  │    │   Pub/Sub   │    │  Consumer   │
│ Carts API   │───▶│ (60s cycle) │───▶│ carts-events│───▶│ Process &   │
│             │    │ Event Gen   │    │   Topic     │    │ Store JSONL │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                          │                                      │
                    ┌─────▼───────┐                        ┌─────▼─────┐
                    │ Cart → Event│                        │ GCS →     │
                    │ Conversion  │                        │ BigQuery  │
                    │ w/ Metadata │                        │ Raw Store │
                    └─────────────┘                        └───────────┘
```

**API Poller**: Continuously fetches cart data, converts each cart to structured events with metadata (event ID, timestamp, cart metrics).  
**Consumer**: Subscribes to events, processes with acknowledgment patterns, stores as JSONL in Cloud Storage and loads to BigQuery.

The API poller runs continuously, fetching cart data every 60 seconds and converting each cart into a structured event with metadata including event ID, extraction timestamp, and cart metrics. The consumer process subscribes to cart events and processes them by saving the event data to Cloud Storage in JSONL format, implementing proper acknowledgment patterns to ensure message processing guarantees.


## How dbt Transformation Works

dbt orchestrates a two-stage transformation pipeline that converts raw JSON data into an analytics-ready star schema designed for business intelligence and reporting.

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Raw Data  │      │   Staging   │      │    Marts    │
│  (BigQuery  │ ────▶│   Models    │ ────▶│ Dimensional │
│   bq_raw)   │      │             │      │   Schema    │
└─────────────┘      └─────────────┘      └─────────────┘
                            │                     │
                    ┌───────▼───────┐    ┌────────▼────────┐
                    │ • stg_products│    │ • dim_products  │
                    │ • stg_users   │    │ • dim_users     │
                    │ • stg_cart_   │    │ • fact_orders   │
                    │   events      │    │   (star schema) │
                    └───────────────┘    └─────────────────┘
```

**Staging Layer**: Cleans and standardizes raw JSON data with type casting, null handling, and basic transformations to prepare for analytics consumption.

**Marts Layer**: Implements star schema with dimension tables (products, users) and fact table (orders) optimized for analytical queries and business intelligence tools.

**Output**: Creates 6 models in BigQuery bq_analytics dataset:
- **Staging Views**: stg_products, stg_users, stg_cart_events
- **Dimension Tables**: dim_products, dim_users
- **Fact Table**: fact_orders (partitioned by date)


## Assumptions & Limitations

This implementation makes several architectural assumptions that influence design decisions and operational characteristics. The system assumes the FakeStore API provides stable and consistent data structures that match the defined Pydantic models, with reliable network connectivity and appropriate error handling for transient failures.

### Design Assumptions
- **FakeStore API**: Reliable public API with consistent data structure
- **GCP Infrastructure**: Provisioned BigQuery, GCS, Pub/Sub resources
- **Data Freshness**: Daily batch updates acceptable for products/users
- **Data Format**: JSONL optimal for BigQuery loading

### Current Implementation
- **Full Refresh**: Batch pipeline reloads all data daily (idempotent)
- **Streaming Pattern**: API polling simulates real-time events
- **Analytics Focus**: Star schema optimized for BI and reporting

### Production Enhancements
For enterprise deployment, consider:
- **Incremental Processing**: CDC or timestamp-based incremental loads
- **True Streaming**: Replace API polling with webhooks/Kafka
- **Monitoring**: Add DataDog/GCP Monitoring for pipeline health
- **Data Quality**: Implement Great Expectations or similar framework
- **CI/CD**: Automated testing and deployment pipelines
- **Secret Management**: Google Secret Manager integration