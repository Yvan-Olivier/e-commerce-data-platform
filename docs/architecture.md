# EY Data Platform Architecture

## Overview
Production-oriented data platform on Google Cloud Platform.

## Components
- **Ingestion**: Batch and streaming data ingestion
- **Storage**: Raw data in GCS, processed data in BigQuery
- **Transformation**: dbt for analytics-ready tables
- **Infrastructure**: Terraform for GCP resources

## Data Flow
```
APIs → Ingestion → GCS (raw) → BigQuery → dbt → Analytics Tables
```