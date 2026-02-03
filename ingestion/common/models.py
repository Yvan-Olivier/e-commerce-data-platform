"""Models for data validation."""
from datetime import datetime
from typing import List, Dict, Any
from pydantic import BaseModel

class Product(BaseModel):
    """Product from FakeStore API (batch)."""
    id: int
    title: str
    price: float
    description: str
    category: str
    image: str

class User(BaseModel):
    """User from FakeStore API (batch)."""
    id: int
    email: str
    username: str
    name: Dict[str, str]  # firstName, lastName
    phone: str
    address: Dict[str, Any]

class CartItem(BaseModel):
    """Item in a cart."""
    productId: int
    quantity: int

class Cart(BaseModel):
    """Cart data (streaming)."""
    id: int
    userId: int
    date: datetime
    products: List[CartItem]