"""
Carts API poller for streaming ingestion.

Polls the FakeStore API for carts and publishes events to Pub/Sub.
"""
import json
import time
import logging
import uuid
from datetime import datetime, timezone
from typing import Set
from google.cloud import pubsub_v1

from ..common.config import settings
from ..common.api_client import FakeStoreClient

logger = logging.getLogger(__name__)


class CartsPoller:
    """Polls the carts API and publishes events to Pub/Sub."""
    
    def __init__(self):
        self.api_client = FakeStoreClient()
        self.publisher = pubsub_v1.PublisherClient()
        self.topic_path = self.publisher.topic_path(
            settings.GCP_PROJECT_ID, 
            settings.PUBSUB_TOPIC_CARTS
        )
        self.poll_interval = settings.CARTS_POLL_INTERVAL_SECONDS
        
        # Track processed cart IDs to avoid duplicates
        self.processed_cart_ids: Set[int] = set()
        
        logger.info(f"CartsPoller initialized")
        logger.info(f"Topic: {self.topic_path}")
        logger.info(f"Poll interval: {self.poll_interval} seconds")
    
    def poll_carts(self) -> None:
        """Poll the carts API and publish new carts to Pub/Sub."""
        try:
            logger.info("Polling carts API...")
            carts = self.api_client.get_carts()
            logger.info(f"Retrieved {len(carts)} carts from API")
            
            new_carts = []
            for cart in carts:
                if cart.id not in self.processed_cart_ids:
                    new_carts.append(cart)
                    self.processed_cart_ids.add(cart.id)
            
            if new_carts:
                logger.info(f"Found {len(new_carts)} new carts to publish")
                self._publish_carts(new_carts)
            else:
                logger.info("No new carts found")
                
        except Exception as e:
            logger.error(f"Error polling carts: {str(e)}")
    
    def _publish_carts(self, carts) -> None:
        """Publish cart events to Pub/Sub."""
        published_count = 0
        now = datetime.now(timezone.utc)
        
        for cart in carts:
            try:
                # Create simple cart event for analytics - focus on key metrics
                event = {
                    "event_id": str(uuid.uuid4()),
                    "event_type": "cart_created", 
                    "extracted_at": now.isoformat(),
                    "published_at": now.isoformat(),
                    "cart_id": cart.id,
                    "user_id": cart.userId,
                    "cart_date": cart.date.isoformat(),
                    "total_items": sum(p.quantity for p in cart.products)
                }
                
                message_data = json.dumps(event).encode('utf-8')
                self.publisher.publish(self.topic_path, message_data)
                
                logger.info(f"Published cart {cart.id}")
                published_count += 1
                
            except Exception as e:
                logger.error(f"Failed to publish cart {cart.id}: {e}")
        
        logger.info(f"Published {published_count}/{len(carts)} carts")
    
    def run(self) -> None:
        """Start the polling loop."""
        logger.info("Starting carts polling service...")
        logger.info(f"Will poll every {self.poll_interval} seconds")
        
        try:
            while True:
                start_time = time.time()
                
                # Poll for carts
                self.poll_carts()
                
                # Calculate sleep time to maintain consistent interval
                elapsed_time = time.time() - start_time
                sleep_time = max(0, self.poll_interval - elapsed_time)
                
                if sleep_time > 0:
                    logger.info(f"Polling completed in {elapsed_time:.2f}s, sleeping for {sleep_time:.2f}s")
                    time.sleep(sleep_time)
                else:
                    logger.warning(f"Polling took {elapsed_time:.2f}s, longer than interval {self.poll_interval}s")
                    
        except KeyboardInterrupt:
            logger.info("Stopping carts polling service...")
        except Exception as e:
            logger.error(f"Fatal error in polling service: {str(e)}")
            raise


def main():
    """Main entry point for the carts poller service."""
    # Setup basic logging
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        poller = CartsPoller()
        poller.run()
    except Exception as e:
        logger.error(f"Failed to start carts poller: {str(e)}")
        raise


if __name__ == "__main__":
    main()