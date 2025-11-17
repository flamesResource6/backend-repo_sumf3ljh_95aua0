"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Embrovia-specific schemas

class Inquiry(BaseModel):
    """
    Customer inquiries and quote requests
    Collection name: "inquiry"
    """
    name: str = Field(..., description="Customer name")
    email: EmailStr = Field(..., description="Customer email")
    company: Optional[str] = Field(None, description="Company or brand name")
    whatsapp: Optional[str] = Field(None, description="WhatsApp number for quick replies")
    service: str = Field(..., description="Requested service (digitizing, patches, vector, logo-redraw)")
    message: Optional[str] = Field(None, description="Extra details provided by customer")
    country: Optional[str] = Field(None, description="Customer country")
    quantity: Optional[int] = Field(None, ge=1, description="Estimated quantity for patches/orders")
    turnaround: Optional[str] = Field(None, description="Requested turnaround time")
    file_names: Optional[List[str]] = Field(default=None, description="Uploaded file names associated with request")
