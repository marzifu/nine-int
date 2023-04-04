from .database import Base
from sqlalchemy import ForeignKey, column, false, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import Column, Integer, String, ARRAY, Boolean, TIMESTAMP

class Payment(Base):
    __tablename__ = "payment"

    order_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    order_details = Column(JSONB, nullable=False)
    # item id
    # price
    # item name
    # quantity
    customer_details = Column(JSONB)
    # first_name
    # last_name 
    # email  
    # phone 
    billing_address = Column(JSONB)
    # Content Billing Address
    # first name
    # last name
    # address
    # city
    # postal_code
    shipping_address = Column(JSONB)
    # Content Shipping Address
    # first name
    # last name
    # address
    # city
    # postal_code
    createdAt = Column(TIMESTAMP(timezone=True), server_default=text("now()"))

class Items(Base):
    __tablename__ = "items"

    item_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    price = Column(Integer, nullable=False)
    item_name = Column(String, nullable=False)
    createdAt = Column(TIMESTAMP(timezone=True), server_default=text("now()"))