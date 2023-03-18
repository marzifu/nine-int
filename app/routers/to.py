
from datetime import datetime
from fastapi import HTTPException, Response, status
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemasTO as schemas, modelsTO as models, auth

routers = APIRouter(
    prefix="/tryouts",
    tags=['Tryout']
)

@routers.get("", response_model=List[schemas.Tryout])
def get_to(db: Session = Depends(get_db)):
    to_get = db.query(models.mainTO).all()
    return to_get

@routers.get("/taken")
def get_taken(db: Session = Depends(get_db), current_user: int = Depends (auth.current_user)):
    taken_get = db.query(models.takenTO).filter(models.takenTO.user_id == current_user.user_id).all()
    to_details = []
    for idz in taken_get:
        main_to = db.query(models.mainTO).filter(models.mainTO.to_id == idz.to_id, models.mainTO.startsAt > datetime.now()).scalar()
        to_details.append(main_to)
    payload = []
    counter = 0
    while counter < len(to_details):
        if to_details[counter] != None:
            data = {
                "to_details": to_details[counter],
                "taken_details": taken_get[counter]
            }
            counter+=1
            payload.append(data)
        else:
            counter+=1
    return payload

@routers.get("/{to_slug}", response_model=schemas.Tryout)
def get_to(to_slug: str, db: Session = Depends(get_db)):
    data_to = db.query(models.mainTO).filter(models.mainTO.to_slug == to_slug).first()
    return data_to

@routers.get("/{to_slug}/soal", response_model=List[schemas.getSoal])
def get_soal(to_slug: str, db: Session = Depends(get_db)):
    id_to = db.query(models.mainTO.to_id).filter(models.mainTO.to_slug == to_slug).limit(1).scalar()
    data_soal = db.query(models.soalTO).filter(models.soalTO.to_id == id_to).all()
    return data_soal

@routers.get("/{to_slug}/soal/admin", response_model=List[schemas.Soal])
def get_soal(to_slug: str, db: Session = Depends(get_db)):
    id_to = db.query(models.mainTO.to_id).filter(models.mainTO.to_slug == to_slug).limit(1).scalar()
    data_soal = db.query(models.soalTO).filter(models.soalTO.to_id == id_to).all()
    return data_soal

@routers.post("/{to_slug}/soal", response_model=List[schemas.Soal])
def create_soal(to_slug:str, soal:List[schemas.Soal], db: Session = Depends(get_db)):
    objects = []
    for soals in soal:
        id_dict = db.query(models.mainTO.to_id).filter(models.mainTO.to_slug == to_slug).scalar()
        id_soal = db.query(models.soalTO).filter(models.soalTO.to_id == id_dict).all()
        for id in id_soal:
            tba_del = db.query(models.soalTO).filter(models.soalTO.soal_id == id.soal_id).limit(1).scalar()
            db.delete(tba_del)
            db.commit()
        soal_create = models.soalTO(to_id=id_dict, **soals.dict())
        objects.append(soal_create)
    db.bulk_save_objects(objects)
    db.commit()
    return objects

@routers.post("/create", response_model=schemas.Tryout)
def create_to(create: schemas.Tryout, db: Session = Depends(get_db)):
    to_create = models.mainTO(**create.dict())
    db.add(to_create)
    db.commit()
    db.refresh(to_create)
    return to_create

@routers.post("/take/{to_slug}", response_model=schemas.Taken)
def take_to(to_slug: str, take: schemas.Taken, db: Session = Depends(get_db), current_user: int = Depends(auth.current_user)):
    current_to = db.query(models.mainTO.to_id).filter(models.mainTO.to_slug == to_slug).scalar()
    taken_to = db.query(models.takenTO.to_id).filter(models.takenTO.to_id == current_to).limit(1).scalar()
    user_exist = str(db.query(models.takenTO.user_id).filter(models.takenTO.user_id == current_user.user_id).limit(1).scalar())
    current = str(current_user.user_id)
    if current_to == taken_to and user_exist == current:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"You have taken this tryout")
    to_taken = models.takenTO(user_id=current_user.user_id,to_id=current_to, type=take.type)
    db.add(to_taken)
    db.commit()
    db.refresh(to_taken)
    return to_taken

@routers.post("/{to_slug}/submit")
def submit_to(to_slug: str, jawab: schemas.Jawab, db: Session = Depends(get_db), current_user: int = Depends(auth.current_user)):
    current = str(current_user.user_id)
    id_to = db.query(models.mainTO.to_id).filter(models.mainTO.to_slug == to_slug).scalar()
    id_taken = db.query(models.takenTO.taken_id).filter(models.takenTO.to_id == id_to).limit(1).scalar()
    taken_user = db.query(models.takenTO.taken_id).filter(models.takenTO.user_id == current_user.user_id, models.takenTO.to_id == (id_to)).limit(1).scalar()
    user_exist = str(db.query(models.takenTO.user_id).filter(models.takenTO.user_id == current_user.user_id).limit(1).scalar())
    #Checking if user exists in the taken table
    if current == user_exist and id_taken == taken_user:
        correct = 0
        false = 0
        user_answer = models.draftTO(to_id=id_to, user_id=current_user.user_id, **jawab.dict())
        draft_content = db.query(models.draftTO).filter(models.draftTO.user_id == current_user.user_id).limit(1).scalar()
        draft_user = db.query(models.draftTO.user_id).filter(models.draftTO.user_id == current_user.user_id).limit(1).scalar()
        #Checking if the current user exists in the draft table
        if current == str(draft_user):
            db.delete(draft_content)
            db.commit()
            db.add(user_answer)
            db.commit()
        else:
            db.add(user_answer)
            db.commit()
        correction = db.query(models.draftTO.user_answers).scalar()
        #Main correction function
        ansIds = []
        cor = []
        counter = 0
        for corr in correction:
            cor.append(corr['answer'])
            ansIds.append(corr['soal_id'])
        while counter < len(cor):
            if db.query(models.soalTO.correctAns).filter(models.soalTO.soal_id == ansIds[counter]).limit(1).scalar() == cor[counter]:
                correct+=1
                counter+=1
            else:
                false+=1
                counter+=1
        counter = 0    
        finalScore = correct * 2
        final = models.hasilTO(user_id=current, to_id=id_to, taken_id=id_taken, totalCorrect=correct, totalFalse=false, score=finalScore)
        #Final check if user in hasil table exists with the hasil id existing
        hasil_exist = db.query(models.hasilTO.hasil_id).filter(models.hasilTO.taken_id == taken_user).limit(1).scalar()
        to_hasil = db.query(models.hasilTO).filter(models.hasilTO.user_id == current_user.user_id, models.hasilTO.hasil_id == hasil_exist, models.hasilTO.to_id == id_to).scalar()
        if to_hasil != None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You have already submitted this tryout")
        else:
            db.add(final)
            db.commit()
            db.refresh(final)
            return final
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User conflict - return to menu")

@routers.delete("/remove/{to_slug}")
def drop_to(to_slug: str, db: Session = Depends(get_db),current_user: int = Depends(auth.current_user)):
    taken_query = db.query(models.takenTO).filter(models.mainTO.to_slug == to_slug).limit(1).scalar()
    taken_to = taken_query
    
    if taken_to == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"You have not taken this tryout yet")
    
    if str(taken_to.user_id) != str(current_user.user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform action")
    
    db.delete(taken_to)
    db.commit()
   
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@routers.delete("/delete/{to_slug}")
def delete_to(to_slug:str, db: Session = Depends(get_db), current_user: int = Depends(auth.current_user)):
    tryout_slug = db.query(models.mainTO).filter(models.mainTO.to_slug == to_slug).limit(1).scalar()

    if tryout_slug == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No tryouts found")
    else:
        db.delete(tryout_slug)
        db.commit()

@routers.delete("/results")
def result(db: Session = Depends(get_db), current_user: int = Depends(auth.current_user)):
    results = db.query(models.hasilTO).filter(models.hasilTO.user_id == current_user.user_id).all()
    return results