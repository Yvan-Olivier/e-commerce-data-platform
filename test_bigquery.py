"""Test BigQuery data loading."""
from google.cloud import bigquery
from ingestion.common.config import settings

def test_bigquery_data():
    """Test that data was loaded correctly to BigQuery."""
    client = bigquery.Client(project=settings.GCP_PROJECT_ID)
    
    # Test products table
    products_query = f"""
    SELECT COUNT(*) as count 
    FROM `{settings.GCP_PROJECT_ID}.{settings.BQ_RAW_DATASET}.Products`
    """
    products_result = list(client.query(products_query))[0]
    print(f"✅ Products in BigQuery: {products_result.count}")
    
    # Test users table  
    users_query = f"""
    SELECT COUNT(*) as count
    FROM `{settings.GCP_PROJECT_ID}.{settings.BQ_RAW_DATASET}.Users`
    """
    users_result = list(client.query(users_query))[0]
    print(f"✅ Users in BigQuery: {users_result.count}")
    
    # Sample data check
    sample_query = f"""
    SELECT title, price, category 
    FROM `{settings.GCP_PROJECT_ID}.{settings.BQ_RAW_DATASET}.Products` 
    LIMIT 3
    """
    print(f"\n✅ Sample products:")
    for row in client.query(sample_query):
        print(f"  - {row.title}: ${row.price} ({row.category})")

if __name__ == "__main__":
    test_bigquery_data()