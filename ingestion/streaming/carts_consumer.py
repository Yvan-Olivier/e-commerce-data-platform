"""
Carts consumer for streaming ingestion.

Consumes cart events from Pub/Sub and streams directly to BigQuery.
"""
import json
import logging
from google.cloud import pubsub_v1, bigquery

from ..common.config import settings

logger = logging.getLogger(__name__)


class CartsConsumer:
    """Consumes cart events from Pub/Sub and streams to BigQuery."""
    
    def __init__(self):
        self.subscriber = pubsub_v1.SubscriberClient()
        self.bq_client = bigquery.Client()
        self.table_ref = f"{settings.GCP_PROJECT_ID}.{settings.BQ_RAW_DATASET}.carts_events"
        
        self.subscription_path = self.subscriber.subscription_path(
            settings.GCP_PROJECT_ID, 
            settings.PUBSUB_SUBSCRIPTION_CARTS
        )
        
        logger.info(f"CartsConsumer initialized")
        logger.info(f"Subscription: {self.subscription_path}")
        logger.info(f"BigQuery Table: {self.table_ref}")
    
    def process_message(self, message):
        """Process a single Pub/Sub message and stream to BigQuery."""
        try:
            # Parse event data
            event_data = json.loads(message.data.decode('utf-8'))
            
            logger.info(f"Received cart event: {event_data['cart_id']}")
            
            # Stream to BigQuery
            errors = self.bq_client.insert_rows_json(
                self.bq_client.get_table(self.table_ref), 
                [event_data]
            )
            
            if errors:
                logger.error(f"BigQuery insert failed: {errors}")
                message.nack()
            else:
                logger.info(f"Streamed cart {event_data['cart_id']} to BigQuery")
                message.ack()
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            message.nack()
    
    def run(self):
        """Start consuming messages from Pub/Sub."""
        logger.info("Starting BigQuery streaming consumer...")
        
        try:
            streaming_pull_future = self.subscriber.subscribe(
                self.subscription_path,
                callback=self.process_message,
                flow_control=pubsub_v1.types.FlowControl(max_messages=10)
            )
            
            logger.info("Listening for messages...")
            
            try:
                streaming_pull_future.result()
            except KeyboardInterrupt:
                streaming_pull_future.cancel()
                logger.info("Consumer stopped.")
                        
        except Exception as e:
            logger.error(f"Error in consumer: {e}")
            raise


def main():
    """Main entry point for the carts consumer service."""
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        consumer = CartsConsumer()
        consumer.run()
    except Exception as e:
        logger.error(f"Failed to start consumer: {e}")
        raise


if __name__ == "__main__":
    main()