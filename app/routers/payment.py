from datetime import datetime, timedelta
from fastapi import HTTPException, Response, status
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import null
from sqlalchemy.orm import Session
from ..database import get_db
from .. import midtrans

routers = APIRouter(
    prefix="/payment",
    tags=['Payment']
)

@routers.post('/payment')
def payment(amount: int):
    payment_url = midtrans.create_transaction(
        order_id='your_order_id',
        gross_amount=amount,
        item_details=item_details,
        customer_details=customer_details
    )
    return {'payment_url': payment_url}