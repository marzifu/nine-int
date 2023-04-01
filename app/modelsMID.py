from .database import Base
from sqlalchemy import ForeignKey, column, false, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import Column, Integer, String, ARRAY, Boolean, TIMESTAMP

class Payment(Base):
    __tablename__ = "payment"

    order_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    order_details = Column(JSONB, nullable=False)
    createdAt = Column(TIMESTAMP(timezone=True), server_default=text("now()"))