"""Quick test for API client."""
from ingestion.common.api_client import FakeStoreClient

def test_api_client():
    """Test that API client works and models validate correctly."""
    client = FakeStoreClient()
    
    # Test products
    print("Fetching products...")
    products = client.get_products()
    print(f"✅ Got {len(products)} products")
    print(f"First product: {products[0].title}")
    
    # Test users  
    print("\nFetching users...")
    users = client.get_users()
    print(f"✅ Got {len(users)} users")
    print(f"First user: {users[0].username}")

if __name__ == "__main__":
    test_api_client()