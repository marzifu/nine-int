from .database import Base
from sqlalchemy import Float, ForeignKey, column, false, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import Column, Integer, String, ARRAY, Boolean, TIMESTAMP

class Payment(Base):
    __tablename__ = "payment"

    payment_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    order_id = Column(UUID(as_uuid=True), nullable=False, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    status = Column(String, nullable=False, server_default="pending")
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

class midtransHandling(Base):
    __tablename__ = "midtransHandling"

    handling_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    order_id = Column(UUID(as_uuid=True), nullable=False)
    merchant_id = Column(String, nullable=False)
    gross_amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    transaction_status = Column(String, nullable=False)
    status_code = Column(String, nullable=False)
    transaction_id = Column(String, nullable=False)

class Items(Base):
    __tablename__ = "items"

    item_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    price = Column(Integer, nullable=False)
    item_name = Column(String, nullable=False)
    createdAt = Column(TIMESTAMP(timezone=True), server_default=text("now()"))