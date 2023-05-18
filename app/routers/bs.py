from datetime import datetime, timedelta
from fastapi import HTTPException, Response, status
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import null
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemasBS as schemas, modelsBS as models, auth

routers = APIRouter(
    prefix="/banksoal",
    tags=['Bank Soal']
)

@routers.post("/create", response_model=schemas.BankSoal)
def create_bs(buat: schemas.BankSoal, db: Session = Depends(get_db)):
    bs_create = models.mainBS(**buat.dict())
    db.add(bs_create)
    db.commit()
    return bs_create

@routers.get("", response_model=List[schemas.BankSoal])
def get_bs(db: Session = Depends(get_db)):
    bs_get = db.query(models.mainBS).all()
    return bs_get

@routers.get("/taken")
def get_taken(db: Session = Depends(get_db), current_user: int = Depends (auth.current_user)):
    taken_get = db.query(models.takenBS).filter(models.takenBS.user_id == current_user.user_id).all()
    bs_taken = []
    for idz in taken_get:
        main_bs = db.query(models.mainBS).filter(models.mainBS.bs_id == idz.bs_id).scalar()
        bs_taken.append(main_bs)
    payload = []
    counter = 0
    while counter < len(bs_taken):
        data = {
            "bs_details": bs_taken[counter],
            "taken_details": taken_get[counter]
        }
        counter+=1
        payload.append(data)
    return payload

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
    id_dict = db.query(models.mainBS.bs_id).filter(models.mainBS.bs_slug == bs_slug).scalar()
    for soals in soal:
        soal_create = models.soalBS(bs_id=id_dict, **soals.dict())
        #Kalau data yang dikirim answernya kosong dan punya soal_id maka delete soal tsb!
        if soal_create.answers == [] and soal_create.soal_id != null:
            id_soal = db.query(models.soalBS).filter(models.soalBS.soal_id == soal_create.soal_id)
            for id in id_soal:
                tba_del = db.query(models.soalBS).filter(models.soalBS.soal_id == id.soal_id).limit(1).scalar()
                db.delete(tba_del)
                db.commit()
        #Kalau data yang dikirim memiliki soal_id dan tidak ada data kosong maka update!
        elif soal_create.soal_id != null:
            id_soal = db.query(models.soalBS).filter(models.soalBS.soal_id == soal_create.soal_id)
            for id in id_soal:
                tba_del = db.query(models.soalBS).filter(models.soalBS.soal_id == id.soal_id).limit(1).scalar()
                db.delete(tba_del)
                db.commit()
            objects.append(soal_create)
        #Kalau data tidak memiliki soal_id dan tidak ada data kosong maka post data baru!
        else:
            id_soal = db.query(models.soalBS).filter(models.soalBS.bs_id == id_dict)
            for id in id_soal:
                tba_del = db.query(models.soalBS).filter(models.soalBS.soal_id == id.soal_id).limit(1).scalar()
                db.delete(tba_del)
                db.commit()
            objects.append(soal_create)
    db.bulk_save_objects(objects)
    db.commit()
    return objects

@routers.post("/take/{bs_slug}")
def take_bs(bs_slug: str, db: Session = Depends(get_db), current_user: int = Depends(auth.current_user)):
    current = str(current_user.user_id)
    current_bs = db.query(models.mainBS.bs_id).filter(models.mainBS.bs_slug == bs_slug).scalar()
    taken_bs = db.query(models.takenBS.bs_id).filter(models.takenBS.bs_id == current_bs, models.takenBS.user_id == current).limit(1).scalar()
    user_exist = str(db.query(models.takenBS.user_id).filter(models.takenBS.user_id == current_user.user_id).limit(1).scalar())
    if current_bs == taken_bs and user_exist == current:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"You have taken this bank soal")
    bs_taken = models.takenBS(user_id=current_user.user_id,bs_id=current_bs)
    db.add(bs_taken)
    db.commit()
    db.refresh(bs_taken)
    return bs_taken

@routers.post("/{bs_slug}/submit")
def submit_bs(bs_slug: str, jawab: schemas.Jawab, db: Session = Depends(get_db), current_user: int = Depends(auth.current_user)):
    current = str(current_user.user_id)
    id_bs = db.query(models.mainBS.bs_id).filter(models.mainBS.bs_slug == bs_slug).scalar()
    id_taken = db.query(models.takenBS.taken_id).filter(models.takenBS.user_id == current_user.user_id, models.takenBS.bs_id == (id_bs)).limit(1).scalar()
    user_exist = str(db.query(models.takenBS.user_id).filter(models.takenBS.user_id == current_user.user_id).limit(1).scalar())
    #Checking if user exists in the taken table
    if current == user_exist and id_taken != None:
        correct = 0
        false = 0
        user_answer = models.draftBS(bs_id=id_bs, user_id=current_user.user_id, **jawab.dict())
        draft_content = db.query(models.draftBS).filter(models.draftBS.user_id == current_user.user_id, models.draftBS.bs_id == id_bs).limit(1).scalar()
        draft_user = db.query(models.draftBS.user_id).filter(models.draftBS.user_id == current_user.user_id, models.draftBS.bs_id == id_bs).limit(1).scalar()
        #Checking if the current user exists in the draft table
        if current == str(draft_user):
            db.delete(draft_content)
            db.commit()
            db.add(user_answer)
            db.commit()
        else:
            db.add(user_answer)
            db.commit()
            db.refresh()
        correction = db.query(models.draftBS.user_answers).filter(models.draftBS.user_id == current, models.draftBS.bs_id == id_bs).scalar()
        #Main correction function
        ansIds = []
        cor = []
        #Variables for Pembahasan
        pembahasan = []
        counter = 0
        for corr in correction:
            cor.append(corr['answer'])
            ansIds.append(corr['soal_id'])
        while counter < len(cor):
            if db.query(models.soalBS.correctAns).filter(models.soalBS.soal_id == ansIds[counter]).limit(1).scalar() == cor[counter]:
                correct_ans = {"soal_id": ansIds[counter], "answer": cor[counter], "detail": "correct"}
                pembahasan.append(correct_ans)
                correct+=1
                counter+=1
            else:
                false_ans = {"soal_id": ansIds[counter], "answer": cor[counter], "detail": "false"}
                pembahasan.append(false_ans)
                false+=1
                counter+=1
        counter = 0    
        finalScore = correct * 2
        final = models.hasilBS(user_id=current, bs_id=id_bs, taken_id=id_taken, bstalCorrect=correct, bstalFalse=false, score=finalScore)
        bahas = models.bahasBS(user_id=current, bs_id=id_bs, user_answers=pembahasan)
        #Final check if user in hasil table exists with the hasil id existing
        hasil_exist = db.query(models.hasilBS.hasil_id).filter(models.hasilBS.taken_id == id_taken).limit(1).scalar()
        bs_hasil = db.query(models.hasilBS).filter(models.hasilBS.user_id == current_user.user_id, models.hasilBS.hasil_id == hasil_exist, models.hasilBS.bs_id == id_bs).scalar()
        if bs_hasil != None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You have already submitted this bank soal")
        else:
            db.add(bahas)
            db.commit()
            db.add(final)
            db.commit()
            db.refresh(final)
            return final
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User conflict - return bs menu")

@routers.delete("/remove/{bs_slug}")
def drop_bs(bs_slug: str, db: Session = Depends(get_db),current_user: int = Depends(auth.current_user)):
    taken_query = db.query(models.takenBS).filter(models.mainBS.bs_slug == bs_slug, models.takenBS.user_id == current_user.user_id).limit(1).scalar()
    taken_bs = taken_query
    
    if taken_bs == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"You have not taken this bank soal yet")
    
    if str(taken_bs.user_id) != str(current_user.user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized bs perform action")
    
    db.delete(taken_bs)
    db.commit()
   
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@routers.delete("/delete/{bs_slug}")
def delete_bs(bs_slug:str, db: Session = Depends(get_db), current_user: int = Depends(auth.current_user)):
    banksoal_slug = db.query(models.mainBS).filter(models.mainBS.bs_slug == bs_slug).limit(1).scalar()

    if banksoal_slug == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No bank soals found")
    else:
        db.delete(banksoal_slug)
        db.commit()

@routers.get("/results")
def result(db: Session = Depends(get_db), current_user: int = Depends(auth.current_user)):
    results = db.query(models.hasilBS).filter(models.hasilBS.user_id == current_user.user_id).all()
    return results

@routers.get("/check/{bs_slug}")
def check(bs_slug: str, db: Session = Depends(get_db), current_user: int = Depends(auth.current_user)):
    id_bs = db.query(models.mainBS.bs_id).filter(models.mainBS.bs_slug == bs_slug).scalar()
    hasil_exist = db.query(models.hasilBS.hasil_id).filter(models.hasilBS.user_id == current_user.user_id, models.hasilBS.bs_id == id_bs).scalar()
    user_check = db.query(models.hasilBS).filter(models.hasilBS.user_id == current_user.user_id, models.hasilBS.hasil_id == hasil_exist, models.hasilBS.bs_id == id_bs).scalar()

    if user_check != None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have submitted this bank soal!")
    
    else:
        return ("Good luck and have fun!")
    
@routers.post("/{bs_slug}/start")
def start(bs_slug:str, db: Session = Depends(get_db), current_user: int = Depends(auth.current_user)):
    id_bs = db.query(models.mainBS.bs_id).filter(models.mainBS.bs_slug == bs_slug).scalar()
    drafts = db.query(models.draftBS).filter(models.draftBS.bs_id == id_bs, models.draftBS.user_id == current_user.user_id).scalar()
    if drafts != None:
        return drafts
    current = current_user.user_id
    draft_create = models.draftBS(bs_id=id_bs, user_id=current)
    db.add(draft_create)
    db.commit()
    db.refresh(draft_create)
    return draft_create

@routers.get("/{bs_slug}/start/retrieve")
def getDraft(bs_slug: str, db: Session = Depends(get_db), current_user: int = Depends(auth.current_user)):
    id_bs = db.query(models.mainBS.bs_id).filter(models.mainBS.bs_slug == bs_slug).scalar()
    drafts = db.query(models.draftBS).filter(models.draftBS.bs_id == id_bs, models.draftBS.user_id == current_user.user_id).scalar()
    return drafts


@routers.post("/{bs_slug}/ongoing")
def ongoing(bs_slug: str, answ: schemas.Draft, db: Session = Depends(get_db), current_user: int = Depends(auth.current_user)):
    id_bs = db.query(models.mainBS.bs_id).filter(models.mainBS.bs_slug == bs_slug).scalar()
    drafts = db.query(models.draftBS.draft_id).filter(models.draftBS.bs_id == id_bs, models.draftBS.user_id == current_user.user_id).scalar()
    draft_content = db.query(models.draftBS).filter(models.draftBS.user_id == current_user.user_id, models.draftBS.bs_id == id_bs).limit(1).scalar()
    add_answers = models.draftBS(draft_id=drafts, bs_id=id_bs, user_id=current_user.user_id, user_answers=answ.user_answers)
    if drafts != None:
        db.delete(draft_content)
        db.commit()
        db.add(add_answers)
        db.commit()
    else:
        db.add(add_answers)
        db.commit()
    return ("Added!")

@routers.get("/{bs_slug}/pembahasan")
def pembahasan(bs_slug: str, db: Session = Depends(get_db), current_user: int = Depends(auth.current_user)):
    id_bs = db.query(models.mainBS.bs_id).filter(models.mainBS.bs_slug == bs_slug).scalar()
    bahas_exist = db.query(models.bahasBS).filter(models.bahasBS.user_id == current_user.user_id, models.bahasBS.bs_id == id_bs).scalar()
    ids = []
    details = []
    user_ans = []
    if bahas_exist != None:
        bahas_answ = db.query(models.bahasBS.user_answers).filter(models.bahasBS.user_id == current_user.user_id, models.bahasBS.bs_id == id_bs).scalar()
        score_bs = db.query(models.hasilBS.score).filter(models.hasilBS.bs_id == id_bs, models.hasilBS.user_id == current_user.user_id).scalar()
        for bhs in bahas_answ:
            ids.append(bhs['soal_id'])
            details.append(bhs['detail'])
            user_ans.append(bhs['answer'])
        payload = []
        counter = 0
        while counter < len(ids):
            list_soal = db.query(models.soalBS).filter(models.soalBS.soal_id == ids[counter]).scalar()
            if list_soal == None:
                counter += 1
            elif list_soal != None:
                data = {
                    "soal_detail": list_soal,
                    "details": details[counter],
                    "user_ans": user_ans[counter],
                    "score": score_bs
                }
                payload.append(data)
                counter+=1
        return payload

    else:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="You haven't completed this bank soal yet.")


