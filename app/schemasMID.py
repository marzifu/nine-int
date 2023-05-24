from datetime import datetime
from typing import Optional
from pydantic import UUID4, BaseModel, EmailStr

class OrderDetails(BaseModel):
    item_id: int
    price: int
    item_name: str

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
    order_details: OrderDetails
    customer_details: CustomerDetails
    billing_address: BillingAddress
    shipping_address: Optional[ShippingAddress] = None

    class Config:
        orm_mode = True

class Items(BaseModel):
    item_id: int
    price: int
    item_name: str

class Handling(BaseModel):
    order_id: str
    merchant_id: str
    gross_amount: float
    currency: str 
    transaction_status: str 
    status_code: str
    transaction_id: str