from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from .. import schemasTO as schemas, modelsTO as models, auth, modelsBS as bs


routers = APIRouter(
    prefix="/admin",
    tags=['Admin']
)

@routers.post("/register", response_model=schemas.Admin)
def add_user(admin: schemas.Users, db: Session = Depends(get_db)):
    hashed_pwd = auth.hash(admin.password)
    admin.password = hashed_pwd
    admin_add = models.Users(**admin.dict())
    db.add(admin_add)
    db.commit()
    db.refresh(admin_add)
    return admin_add

@routers.post("/login")
def log_user(admin: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    login = db.query(models.Users).filter(models.Users.user_email == admin.username).first()
    
    if not login:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")
    
    if not auth.verify(admin.password, login.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")
    
    uid = str(login.user_id)
    access_token = auth.create_token(data = {"admin_id": uid})
    return {"token": access_token, "token_type": "bearer"}