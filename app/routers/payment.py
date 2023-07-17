from datetime import datetime, timedelta, timezone
from pyexpat import model
from fastapi import HTTPException, Response, status
from typing import List
from fastapi import APIRouter, Depends
from pydantic import PaymentCardNumber
from sqlalchemy import asc, desc, null
from sqlalchemy.orm import Session
from ..database import get_db
from .. import midtrans as mid, modelsMID as models, schemasMID as schemas, auth

routers = APIRouter(
    prefix="/payment",
    tags=['Payment']
)

@routers.get("/items")
def items(db: Session = Depends(get_db), current_user: int = Depends(auth.current_user)):
    item = db.query(models.Items).all()
    return item

@routers.get("/items/{id}", response_model=schemas.Items)
def oneItem(id: int, db: Session = Depends(get_db), current_user: int = Depends(auth.current_user)):
    one_items = db.query(models.Items).filter(models.Items.item_id == id).scalar()
    return one_items

#for midtrans handling
@routers.post("/handling")
def handling(handles: schemas.Handling, db: Session = Depends(get_db)):
    if handles.transaction_status == "settlement" or handles.transaction_status == "capture":
        order_post = models.midtransHandling(**handles.dict())
        db.add(order_post)
        db.commit()
        db.refresh(order_post)
    else:
        return {"Data is unchanged"}
    return order_post

@routers.get("/transactions")
def trans_list(db: Session = Depends(get_db), current_user: int = Depends(auth.current_user)):
    transaction_list = db.query(models.Payment).filter(models.Payment.user_id == current_user.user_id).all()
    return transaction_list

@routers.get("/latest")
def latest_trans(db: Session = Depends(get_db), current_user: int = Depends(auth.current_user)):
    trans_latest = db.query(models.Payment).filter(models.Payment.user_id == current_user.user_id).order_by(desc(models.Payment.createdAt)).limit(1).scalar()
    return trans_latest

@routers.put("/update/{order_id}")
def statusUpdate(order_id:str, db: Session = Depends(get_db), current_user: int = Depends(auth.current_user)):
    payments = db.query(models.midtransHandling).filter(models.midtransHandling.order_id == order_id).scalar()
    stat = db.query(models.Payment).filter(models.Payment.order_id == order_id)
    stat.update({"status": payments.transaction_status})
    db.commit()
    return {"Status has been updated Successfully"}

@routers.delete("/delete/{order_id}")
def deleteOrder(order_id:str, db: Session = Depends(get_db), current_user: int = Depends(auth.current_user)):
    payments = db.query(models.Payment).filter(models.Payment.user_id == current_user.user_id, models.Payment.order_id == order_id).scalar()
    if payments == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No payment request has been made")
    else:
        db.delete(payments)
        db.commit()

@routers.post("")
def payment(order: schemas.Payment, db: Session = Depends(get_db), current_user: int = Depends(auth.current_user)):
    current = str(current_user.user_id)
    payments = models.Payment(user_id=current,**order.dict())
    db.add(payments)
    db.commit()
    db.refresh(payments)

    orders = str(db.query(models.Payment.order_id).filter(models.Payment.user_id == current_user.user_id).order_by(desc(models.Payment.createdAt)).limit(1).scalar())
    orderId = []
    orderId.append(orders)

    param = {
            "transaction_details":{
                "order_id": orderId[0],
                "gross_amount": payments.order_details['price']
            },
            "user_id": str(current_user.user_id),
            "order_details": {
                "item_id": payments.order_details['item_id'],
                "price": payments.order_details['price'],
                "item_name": payments.order_details['item_name'],
                "quantity": 1
            },
            "customer_details": {
                "first_name": payments.customer_details['first_name'],
                "last_name": payments.customer_details['last_name'],
                "email": payments.customer_details['email'],
                "phone": payments.customer_details['phone']
            },
            "billing_address": {
                "first_name": payments.billing_address['first_name'],
                "last_name": payments.billing_address['last_name'],
                "address": payments.billing_address['address'],
                "city": payments.billing_address['city'],
                "postal_code": payments.billing_address['postal_code']
            },
            "shipping_address": {
                "first_name": payments.shipping_address['first_name'],
                "last_name": payments.shipping_address['last_name'],
                "address": payments.shipping_address['address'],
                "city": payments.shipping_address['city'],
                "postal_code": payments.shipping_address['postal_code']
            }
    }

    transaction = mid.MidtransAPI.snap.create_transaction(param)
    transaction_token = transaction['token']
    return transaction