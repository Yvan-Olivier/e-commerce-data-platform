"""Configuration for env vars, settings (single source of truth)."""
import os
from dotenv import load_dotenv

load_dotenv()  # Loads .env file

class Settings:
    # GCP
    GCP_PROJECT_ID = os.environ["GCP_PROJECT_ID"]
    GCP_REGION = os.environ.get("GCP_REGION", "europe-west1")
    
    # APIs
    FAKE_STORE_API_URL = os.environ.get("FAKE_STORE_API_URL", "https://fakestoreapi.com")
    API_REQUEST_TIMEOUT = int(os.environ.get("API_REQUEST_TIMEOUT", "30"))
    
    # Storage
    GCS_RAW_BUCKET = os.environ["GCS_RAW_BUCKET"]
    
    # BigQuery
    BQ_RAW_DATASET = os.environ["BQ_RAW_DATASET"]
    BQ_ANALYTICS_DATASET = os.environ["BQ_ANALYTICS_DATASET"]
    
    # Pub/Sub
    PUBSUB_TOPIC_CARTS = os.environ["PUBSUB_TOPIC_CARTS"]
    PUBSUB_SUBSCRIPTION_CARTS = os.environ["PUBSUB_SUBSCRIPTION_CARTS"]
    # Ingestion
    CARTS_POLL_INTERVAL_SECONDS = int(os.environ.get("CARTS_POLL_INTERVAL_SECONDS", "60"))
    BATCH_SCHEDULE_HOUR = int(os.environ.get("BATCH_SCHEDULE_HOUR", "2"))
    
    # Runtime
    ENV = os.environ.get("ENV", "local")
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

settings = Settings()