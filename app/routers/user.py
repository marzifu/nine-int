from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from .. import schemasTO as schemas, modelsTO as models, auth

routers = APIRouter(
    prefix="/users",
    tags=['Users']
)

@routers.get("/", response_model=List[schemas.getUsers])
def get_user(db: Session = Depends(get_db)):
    user_get = db.query(models.Users).all()
    return user_get

@routers.get("/profile", response_model=schemas.getUsers)
def user_by_id(db: Session = Depends(get_db), current_user: int = Depends(auth.current_user)):
    #Menyamakan object dari UUID ke String
    current=str(current_user.user_id)
    user_get = db.query(models.Users).filter(models.Users.user_id == current).first()
    user_db = str(user_get.user_id)
    if current == user_db:
        return user_get
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No permission")
    
    

@routers.post("/register", response_model=schemas.Users)
def add_user(users: schemas.Users, db: Session = Depends(get_db)):
    hashed_pwd = auth.hash(users.password)
    users.password = hashed_pwd
    user_add = models.Users(**users.dict())
    db.add(user_add)
    db.commit()
    db.refresh(user_add)
    return user_add

@routers.post("/login")
def log_user(users: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    login = db.query(models.Users).filter(models.Users.user_email == users.username).first()
    
    if not login:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")
    
    if not auth.verify(users.password, login.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")
    
    uid = str(login.user_id)
    access_token = auth.create_token(data = {"user_id": uid})
    return {"token": access_token, "token_type": "bearer"}