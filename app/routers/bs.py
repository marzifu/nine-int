
from doctest import DocTestFailure
from fastapi import HTTPException, Response, status
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemasBS as schemas, modelsBS as models, auth

routers = APIRouter(
    prefix="/banksoal",
    tags=['Bank Soal']
)

@routers.get("", response_model=List[schemas.BankSoal])
def get_bs(db: Session = Depends(get_db)):
    bs_get = db.query(models.mainBS).all()
    return bs_get

@routers.get("/taken", response_model=List[schemas.getAmbil])
def get_taken(db: Session = Depends(get_db), current_user: int = Depends (auth.current_user)):
    taken_get = db.query(models.takenBS).filter(models.takenBS.user_id == current_user.user_id).all()
    return taken_get

@routers.get("/{bs_slug}", response_model=schemas.BankSoal)
def get_bs(bs_slug: str, db: Session = Depends(get_db)):
    data_bs = db.query(models.mainBS).filter(models.mainBS.bs_slug == bs_slug).first()
    return data_bs

@routers.get("/{bs_slug}/soal", response_model=List[schemas.getSoal])
def get_soal(bs_slug: str, db: Session = Depends(get_db)):
    id_bs = db.query(models.mainBS.bs_id).filter(models.mainBS.bs_slug == bs_slug).limit(1).scalar()
    data_soal = db.query(models.soalBS).filter(models.soalBS.bs_id == id_bs).all()
    return data_soal

@routers.get("/{bs_slug}/soal/admin", response_model=List[schemas.Soal])
def get_soal(bs_slug: str, db: Session = Depends(get_db)):
    id_bs = db.query(models.mainBS.bs_id).filter(models.mainBS.bs_slug == bs_slug).limit(1).scalar()
    data_soal = db.query(models.soalBS).filter(models.soalBS.bs_id == id_bs).all()
    return data_soal

@routers.post("/{bs_slug}/soal", response_model=List[schemas.Soal])
def create_soal(bs_slug:str, soal:List[schemas.Soal], db: Session = Depends(get_db)):
    objects = []
    for soals in soal:
        id_dict = db.query(models.mainBS.bs_id).filter(models.mainBS.bs_slug == bs_slug).scalar()
        soal_create = models.soalBS(bs_id=id_dict, **soals.dict())
        db.add(soal_create)
        id_soal = db.query(models.soalBS.soal_id).all()
        for id in id_soal:
            if soal_create.soal_id == id:
                db.delete(soal_create)
        objects.append(soal_create)
    db.bulk_save_objects(objects)
    db.commit()
    return objects

@routers.post("/create", response_model=schemas.BankSoal)
def create_bs(create: schemas.BankSoal, db: Session = Depends(get_db)):
    bs_create = models.mainBS(**create.dict())
    db.add(bs_create)
    db.commit()
    db.refresh(bs_create)
    return bs_create

@routers.post("/take/{bs_slug}", response_model=schemas.Taken)
def take_bs(bs_slug: str, take: schemas.Taken, db: Session = Depends(get_db), current_user: int = Depends(auth.current_user)):
    current_bs = db.query(models.mainBS.bs_id).filter(models.mainBS.bs_slug == bs_slug).scalar()
    taken_bs = db.query(models.takenBS.bs_id).filter(models.takenBS.bs_id == current_bs).limit(1).scalar()
    user_exist = str(db.query(models.takenBS.user_id).filter(models.takenBS.user_id == current_user.user_id).limit(1).scalar())
    current = str(current_user.user_id)
    if current_bs == taken_bs and user_exist == current:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"You have taken this tryout")
    bs_taken = models.takenBS(user_id=current_user.user_id,bs_id=current_bs, type=take.type)
    db.add(bs_taken)
    db.commit()
    db.refresh(bs_taken)
    return bs_taken

@routers.post("/{bs_slug}/submit")
def submit_bs(bs_slug: str, jawab: schemas.Jawab, db: Session = Depends(get_db), current_user: int = Depends(auth.current_user)):
    current = str(current_user.user_id)
    id_bs = db.query(models.mainBS.bs_id).filter(models.mainBS.bs_slug == bs_slug).scalar()
    id_taken = db.query(models.takenBS.taken_id).filter(models.takenBS.bs_id == id_bs).limit(1).scalar()
    taken_user = db.query(models.takenBS.taken_id).filter(models.takenBS.user_id == current_user.user_id, models.takenBS.bs_id == (id_bs)).limit(1).scalar()
    user_exist = str(db.query(models.takenBS.user_id).filter(models.takenBS.user_id == current_user.user_id).limit(1).scalar())
    #Checking if user exists in the taken table
    if current == user_exist and id_taken == taken_user:
        correct = 0
        false = 0
        user_answer = models.draftBS(bs_id=id_bs, user_id=current_user.user_id, **jawab.dict())
        draft_content = db.query(models.draftBS).filter(models.draftBS.user_id == current_user.user_id).limit(1).scalar()
        draft_user = db.query(models.draftBS.user_id).filter(models.draftBS.user_id == current_user.user_id).limit(1).scalar()
        #Checking if the current user exists in the draft table
        if current == str(draft_user):
            db.delete(draft_content)
            db.commit()
            db.add(user_answer)
            db.commit()
        else:
            db.add(user_answer)
            db.commit()
        correction = db.query(models.draftBS.user_answers).scalar()
        #Main correction function
        ansIds = []
        cor = []
        counter = 0
        for corr in correction:
            cor.append(corr['answer'])
            ansIds.append(corr['soal_id'])
        while counter < len(cor):
            if db.query(models.soalBS.correctAns).filter(models.soalBS.soal_id == ansIds[counter]).limit(1).scalar() == cor[counter]:
                correct+=1
                counter+=1
            else:
                false+=1
                counter+=1
        counter = 0    
        finalScore = correct * 2
        final = models.hasilBS(user_id=current, bs_id=id_bs, taken_id=id_taken, totalCorrect=correct, totalFalse=false, score=finalScore)
        #Final check if user in hasil table exists with the hasil id existing
        hasil_exist = db.query(models.hasilBS.hasil_id).filter(models.hasilBS.taken_id == taken_user).limit(1).scalar()
        bs_hasil = db.query(models.hasilBS).filter(models.hasilBS.user_id == current_user.user_id, models.hasilBS.hasil_id == hasil_exist, models.hasilBS.bs_id == id_bs).scalar()
        if bs_hasil != None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You have already submitted this tryout")
        else:
            db.add(final)
            db.commit()
            db.refresh(final)
            return final
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User conflict - return to menu")

@routers.delete("/remove/{bs_slug}")
def drop_bs(bs_slug: str, db: Session = Depends(get_db),current_user: int = Depends(auth.current_user)):
    taken_query = db.query(models.takenBS).filter(models.mainBS.bs_slug == bs_slug).limit(1).scalar()
    taken_bs = taken_query
    
    if taken_bs == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"You have not taken this tryout yet")
    
    if str(taken_bs.user_id) != str(current_user.user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform action")
    
    db.delete(taken_bs)
    db.commit()
   
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@routers.delete("/delete/{bs_slug}")
def delete_to(bs_slug:str, db: Session = Depends(get_db), current_user: int = Depends(auth.current_user)):
    tryout_slug = db.query(models.mainBS).filter(models.mainBS.bs_slug == bs_slug).limit(1).scalar()

    if tryout_slug == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No tryouts found")
    else:
        db.delete(tryout_slug)
        db.commit()

@routers.delete("/results")
def result(db: Session = Depends(get_db), current_user: int = Depends(auth.current_user)):
    results = db.query(models.hasilTO).filter(models.hasilTO.user_id == current_user.user_id).all()
    return results


