"""API client for FakeStore API."""
import requests
from typing import List, Type, TypeVar
from .config import settings
from .models import Product, User, Cart

T = TypeVar('T')

class FakeStoreClient:
    """Client for FakeStore API."""
    
    def __init__(self):
        self.base_url = settings.FAKE_STORE_API_URL
        self.timeout = settings.API_REQUEST_TIMEOUT
    
    def _fetch_data(self, endpoint: str, model_class: Type[T]) -> List[T]:
        """Generic method to fetch data from API and convert to models."""
        response = requests.get(
            f"{self.base_url}/{endpoint}",
            timeout=self.timeout
        )
        response.raise_for_status()
        
        # Convert JSON to Pydantic models
        return [model_class(**item) for item in response.json()]
    
    def get_products(self) -> List[Product]:
        """Fetch all products from API."""
        return self._fetch_data("products", Product)
    
    def get_users(self) -> List[User]:
        """Fetch all users from API."""
        return self._fetch_data("users", User)
    
    def get_carts(self) -> List[Cart]:
        """Fetch all carts from API."""
        return self._fetch_data("carts", Cart)