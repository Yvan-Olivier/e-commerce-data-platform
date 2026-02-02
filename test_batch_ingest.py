"""Test batch ingestion."""
from ingestion.batch.batch_ingest import BatchIngestion

def test_batch():
    """Test batch ingestion."""
    print("Testing batch ingestion...")
    
    try:
        ingestion = BatchIngestion()
        ingestion.run()
        print("✅ Batch ingestion test completed!")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_batch()