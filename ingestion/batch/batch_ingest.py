"""Batch ingestion for products and users data."""
import json
import logging
from datetime import datetime
from google.cloud import storage
from ..common.api_client import FakeStoreClient
from ..common.config import settings

# Setup logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

class BatchIngestion:
    """Handles batch ingestion of products and users."""
    
    def __init__(self):
        self.client = FakeStoreClient()
        self.gcs_client = storage.Client(project=settings.GCP_PROJECT_ID)
        self.bucket = self.gcs_client.bucket(settings.GCS_RAW_BUCKET)
        
    def ingest_products(self):
        """Fetch and store products data."""
        logger.info("Starting products ingestion...")
        
        # Fetch data
        products = self.client.get_products()
        logger.info(f"Fetched {len(products)} products")
        
        # Convert to JSONL (one object per line for BigQuery)
        products_jsonl = "\n".join([json.dumps(product.model_dump()) for product in products])
        
        # Save to GCS
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        blob_name = f"products/products_{timestamp}.jsonl"
        
        blob = self.bucket.blob(blob_name)
        blob.upload_from_string(products_jsonl)
        
        logger.info(f"✅ Products saved to gs://{settings.GCS_RAW_BUCKET}/{blob_name}")
        
    def ingest_users(self):
        """Fetch and store users data."""
        logger.info("Starting users ingestion...")
        
        # Fetch data
        users = self.client.get_users()
        logger.info(f"Fetched {len(users)} users")
        
        # Convert to JSONL (one object per line for BigQuery)
        users_jsonl = "\n".join([json.dumps(user.model_dump()) for user in users])
        
        # Save to GCS
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        blob_name = f"users/users_{timestamp}.jsonl"
        
        blob = self.bucket.blob(blob_name)
        blob.upload_from_string(users_jsonl)
        
        logger.info(f"✅ Users saved to gs://{settings.GCS_RAW_BUCKET}/{blob_name}")
        
    def run(self):
        """Run full batch ingestion."""
        logger.info("Starting batch ingestion process...")
        
        try:
            self.ingest_products()
            self.ingest_users()
            logger.info("✅ Batch ingestion completed successfully")
        except Exception as e:
            logger.error(f"❌ Batch ingestion failed: {e}")
            raise

def main():
    """Entry point for batch ingestion."""
    ingestion = BatchIngestion()
    ingestion.run()

if __name__ == "__main__":
    main()