"""Batch ingestion for products and users data."""
import json
import logging
from datetime import datetime
from typing import List, Any, Callable
from google.cloud import storage
from ..common.api_client import FakeStoreClient
from ..common.config import settings

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

class BatchIngestion:
    """Handles batch ingestion of products and users."""
    
    def __init__(self):
        self.client = FakeStoreClient()
        self.gcs_client = storage.Client(project=settings.GCP_PROJECT_ID)
        self.bucket = self.gcs_client.bucket(settings.GCS_RAW_BUCKET)
        self.run_date = datetime.now().strftime("%Y-%m-%d")
        
    def _ingest_data(self, data_type: str, fetch_method: Callable) -> None:
        """Fetch data and save to Cloud Storage."""
        logger.info(f"Starting {data_type} ingestion...")
        
        # Fetch data
        data = fetch_method()
        logger.info(f"Fetched {len(data)} {data_type}")
        
        # Generate filename with date
        blob_name = f"{data_type}/{data_type}_{self.run_date}.jsonl"
        
        # Convert to JSONL format
        data_jsonl = "\n".join([json.dumps(item.model_dump()) for item in data])
        
        # Upload to Cloud Storage
        blob = self.bucket.blob(blob_name)
        blob.upload_from_string(data_jsonl)
        
        logger.info(f"✅ {data_type.title()} saved to gs://{settings.GCS_RAW_BUCKET}/{blob_name}")
        
    def ingest_products(self):
        """Fetch and store products data."""
        self._ingest_data("products", self.client.get_products)
        
    def ingest_users(self):
        """Fetch and store users data."""
        self._ingest_data("users", self.client.get_users)
        
    def run(self):
        """Run complete batch ingestion process."""
        logger.info(f"Starting batch ingestion for {self.run_date}...")
        
        try:
            self.ingest_products()
            self.ingest_users()
            logger.info(f"✅ Batch ingestion completed for {self.run_date}")
        except Exception as e:
            logger.error(f"❌ Batch ingestion failed: {e}")
            raise

def main():
    """Entry point for batch ingestion."""
    ingestion = BatchIngestion()
    ingestion.run()

if __name__ == "__main__":
    main()