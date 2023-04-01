from datetime import datetime
from typing import Optional
from pydantic import UUID4, BaseModel, EmailStr

class OrderDetails(BaseModel):
    item_id: int
    price: float
    item_name: str
    quantity: int

class CustomerDetails(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str

class BillingAddress(BaseModel):
    first_name: str
    last_name: str
    address: str
    city: str
    postal_code: int

class ShippingAddress(BaseModel):
    first_name: str
    last_name: str
    address: str
    city: str
    postal_code: int

class Payment(BaseModel):
    order_id: Optional[int] = None
    user_id: Optional[UUID4] = None
    order_details: OrderDetails
    customer_details: CustomerDetails
    billing_address: BillingAddress
    shipping_address: Optional[ShippingAddress] = None

    class Config:
        orm_mode = True