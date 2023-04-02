from datetime import datetime, timedelta
from fastapi import HTTPException, Response, status
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import null
from sqlalchemy.orm import Session
from ..database import get_db
from .. import midtrans as mid, modelsMID as models, schemasMID as schemas

routers = APIRouter(
    prefix="/payment",
    tags=['Payment']
)

@routers.post("")
def testung(order: schemas.Payment, db: Session = Depends(get_db)):
    payments = models.Payment(**order.dict())
    print(payments)

    param = {
        "transaction_details": {
            "order_id": order.order_id,
            "gross_amount": 200000
        }, "credit_card":{
            "secure" : True
        }, "customer_details":{
            "first_name": "budi",
            "last_name": "pratama",
            "email": "budi.pra@example.com",
            "phone": "08111222333"
        }
    }

    transaction = mid.MidtransAPI.snap.create_transaction(param)
    transaction_token = transaction['token']
    return transaction