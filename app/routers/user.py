from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from .. import schemasTO as schemas, modelsTO as models, auth, modelsBS as bs


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
    member = str(login.membership)
    access_token = auth.create_token(data = {"user_id": uid, "membership": member})
    return {"token": access_token, "token_type": "bearer"}

@routers.get("/history")
def history(db: Session = Depends(get_db), current_user: int = Depends(auth.current_user)):
    hasil_to = db.query(models.hasilTO).filter(models.hasilTO.user_id == current_user.user_id).all()
    hasil_bs = db.query(bs.hasilBS).filter(bs.hasilBS.user_id == current_user.user_id).all()
    to_hasil = []
    bs_hasil = []
    to_ids = []
    bs_ids = []
    for idz in hasil_to:
        to_hasil.append(idz)
        to_ids.append(idz.to_id)
    for ids in hasil_bs:
        bs_hasil.append(ids)
        bs_ids.append(ids.bs_id)
    to_cont = []
    bs_cont = []
    contents = {}
    counter = 0
    lenTO = len(to_hasil)
    lenBS = len(bs_hasil)

    if bs_hasil != [] or to_hasil != [] or (bs_hasil == [] and to_hasil == []):
        counter = 0
        while counter < lenTO:
            details_to = db.query(models.mainTO).filter(models.mainTO.to_id == to_ids[counter]).scalar()
            data = {
                "to_hasil": to_hasil[counter],
                "to_details": details_to
            }
            to_cont.append(data)
            counter += 1
        counter = 0
        contents["to_content"] = to_cont
        while counter < lenBS:
            details_bs = db.query(bs.mainBS).filter(bs.mainBS.bs_id == bs_ids[counter]).scalar()
            data = {
                "bs_hasil": bs_hasil[counter],
                "bs_details": details_bs
            }
            bs_cont.append(data)
            counter += 1
        contents["bs_content"] = bs_cont
    # elif bs_hasil != [] and to_hasil == []:
    #     counter = 0
    #     while counter < lenBS:
    #         details_bs = db.query(bs.mainBS).filter(bs.mainBS.bs_id == bs_ids[counter]).scalar()
    #         data = {
    #             "bs_hasil": bs_hasil[counter],
    #             "bs_details": details_bs
    #         }
    #         payload.append(data)
    #         counter += 1
    # elif bs_hasil != [] and to_hasil != []:
    #     while counter < lenTO:
    #         details_to = db.query(models.mainTO).filter(models.mainTO.to_id == to_ids[counter]).scalar()
    #         details_bs = db.query(bs.mainBS).filter(bs.mainBS.bs_id == bs_ids[counter]).scalar()
    #         data = {
    #             "to_hasil": to_hasil[counter],
    #             "bs_hasil": bs_hasil[counter],
    #             "to_details": details_to,
    #             "bs_details": details_bs
    #         }
    #         payload.append(data)
    #         counter += 1
    return contents

@routers.put("/profile/edit")
def edit_profile(user: schemas.UpdateUser ,db: Session = Depends(get_db), current_user: int = Depends(auth.current_user)):
    user_profile = db.query(models.Users).filter(models.Users.user_id == current_user.user_id).scalar()
    user_prof = db.query(models.Users).filter(models.Users.user_id == current_user.user_id)
    if user_profile.user_id == current_user.user_id:
        user_prof.update({"user_name": user.user_name, "phone": user.phone, "address": user.address, "gender": user.gender, "pp_link": user.pp_link}, synchronize_session=False)
        db.commit()
    
    return {"status": 'Success!'}