"""API client for FakeStore API."""
import requests
from typing import List
from .config import settings
from .models import Product, User, Cart

class FakeStoreClient:
    """Client for FakeStore API."""
    
    def __init__(self):
        self.base_url = settings.FAKE_STORE_API_URL
        self.timeout = settings.API_REQUEST_TIMEOUT
    
    def get_products(self) -> List[Product]:
        """Fetch all products from API."""
        response = requests.get(
            f"{self.base_url}/products",
            timeout=self.timeout
        )
        response.raise_for_status()
        
        # Convert JSON to Pydantic models
        return [Product(**item) for item in response.json()]
    
    def get_users(self) -> List[User]:
        """Fetch all users from API."""
        response = requests.get(
            f"{self.base_url}/users", 
            timeout=self.timeout
        )
        response.raise_for_status()
        
        # Convert JSON to Pydantic models
        return [User(**item) for item in response.json()]
    
    def get_carts(self) -> List[Cart]:
        """Fetch all carts from API."""
        response = requests.get(
            f"{self.base_url}/carts",
            timeout=self.timeout
        )
        response.raise_for_status()
        
        # Convert JSON to Pydantic models
        return [Cart(**item) for item in response.json()]