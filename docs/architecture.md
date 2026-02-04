# EY Data Platform Architecture

## Executive Summary

Production-ready data platform built on Google Cloud Platform that ingests e-commerce data from REST APIs, transforms it using dbt, and delivers analytics-ready star schema in BigQuery for business intelligence.

## Architecture Overview

![Architecture Diagram](architecture.mmd)

## Technical Architecture

### Multi-Layer Design

```
APIs → Ingestion → Raw Storage → Transformations → Analytics
```

1. **External APIs**: FakeStore API endpoints (Products, Users, Carts)
2. **Ingestion Layer**: Python-based batch and streaming processors
3. **Raw Storage**: Immutable JSONL files + BigQuery raw tables
4. **Transformation Layer**: dbt staging and marts models
5. **Analytics Layer**: Star schema optimized for BI tools

### Data Ingestion Patterns

#### Batch Processing (Products & Users)
- **Schedule**: Daily (idempotent design)
- **Pattern**: API → GCS → BigQuery
- **Storage**: Date-partitioned JSONL files
- **Volume**: 30 total records (20 products + 10 users)

#### Streaming Processing (Cart Events)
- **Frequency**: 60-second polling
- **Pattern**: API → Pub/Sub → BigQuery
- **Deduplication**: processed_cart_ids tracking
- **Metadata**: event_id, extracted_at, published_at

### Data Models

#### Raw Layer (bq_raw dataset)
- **Products**: Product catalog from FakeStore API
- **Users**: Customer information from FakeStore API
- **carts_events**: Real-time cart activities from streaming pipeline

#### Staging Layer (dbt views)
- **stg_products**: Cleaned product data
- **stg_users**: Standardized user profiles
- **stg_cart_events**: Processed cart events

#### Analytics Layer (bq_analytics dataset)
- **dim_products**: Product dimension table
- **dim_users**: User dimension table
- **fact_orders**: Order facts with date partitioning

## Technology Stack

### Core Technologies
- **Python 3.13**: Primary programming language
- **dbt 1.11**: Data transformation framework
- **Google Cloud Platform**: Cloud infrastructure
- **Pydantic**: Data validation and modeling

### GCP Services
- **BigQuery**: Data warehouse and analytics engine
- **Cloud Storage**: Raw data lake storage
- **Pub/Sub**: Real-time message streaming

## Design Decisions

### Data Reliability
- **Idempotent Processing**: Batch jobs safe to re-run
- **Event Deduplication**: Cart events processed only once
- **Immutable Storage**: Raw data never modified
- **Schema Validation**: Pydantic models ensure data quality

### Scalability
- **Partitioned Tables**: Date-based partitioning for performance
- **Streaming Inserts**: Real-time data availability
- **Cloud-Native**: Leverages managed GCP services

### Code Quality
- **KISS Principle**: Simple, focused components
- **DRY Principle**: No code duplication
- **Version Control**: Complete codebase in Git