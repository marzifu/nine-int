
from datetime import datetime, timedelta, timezone
from math import ceil
import random
from fastapi import HTTPException, Response, status
from typing import Counter, List
from fastapi import APIRouter, Depends
from sqlalchemy import asc, desc, null
from sqlalchemy.orm import Session
from ..database import get_db
from random import choice
from .. import schemasTO as schemas, modelsTO as models, auth

routers = APIRouter(
    prefix="/tryouts",
    tags=['Tryout']
)

@routers.post("/create", response_model=schemas.Tryout)
def create_to(buat: schemas.Tryout, db: Session = Depends(get_db)):
    to_create = models.mainTO(**buat.dict())
    db.add(to_create)
    db.commit()
    return to_create

@routers.get("", response_model=List[schemas.Tryout])
def get_to(db: Session = Depends(get_db)):
    to_get = db.query(models.mainTO).all()
    return to_get

@routers.get("/taken")
def get_taken(db: Session = Depends(get_db), current_user: int = Depends (auth.current_user)):
    taken_get = db.query(models.takenTO).filter(models.takenTO.user_id == current_user.user_id).all()
    to_upcoming = []
    to_ongoing = []
    ids = []
    #Upcoming
    for idz in taken_get:
        main_to = db.query(models.mainTO).filter(models.mainTO.to_id == idz.to_id).scalar()
        if main_to.startsAt > datetime.now(timezone.utc):
            to_upcoming.append(main_to)
        elif main_to.endsAt > datetime.now(timezone.utc) and main_to.startsAt <= datetime.now(timezone.utc):
            to_ongoing.append(main_to)
    payload = []
    counter = 0
    while counter < len(to_upcoming):
        if to_upcoming[counter] != None:
            data = {
                "to_details": to_upcoming[counter],
                "taken_details": taken_get[counter],
                "details": "Upcoming"
            }
            counter+=1
            payload.append(data)
        else:
            counter+=1
            payload.append(data)
    counter = 0
    while counter < len(to_ongoing):
        if to_ongoing[counter] != None:
            data = {
                "to_details": to_ongoing[counter],
                "taken_details": taken_get[counter],
                "details": "Ongoing"
            }
            counter+=1
            payload.append(data)
        else:
            counter+=1
            payload.append(data)
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
    id_dict = db.query(models.mainTO.to_id).filter(models.mainTO.to_slug == to_slug).scalar()
    for soals in soal:
        soal_create = models.soalTO(to_id=id_dict, **soals.dict())
        #Kalau data yang dikirim answernya kosong dan punya soal_id maka delete soal tsb!
        if soal_create.answers == [] and soal_create.soal_id != null:
            id_soal = db.query(models.soalTO).filter(models.soalTO.soal_id == soal_create.soal_id)
            for id in id_soal:
                tba_del = db.query(models.soalTO).filter(models.soalTO.soal_id == id.soal_id).limit(1).scalar()
                db.delete(tba_del)
                db.commit()
        #Kalau data yang dikirim memiliki soal_id dan tidak ada data kosong maka update!
        elif soal_create.soal_id != null:
            id_soal = db.query(models.soalTO).filter(models.soalTO.soal_id == soal_create.soal_id)
            for id in id_soal:
                tba_del = db.query(models.soalTO).filter(models.soalTO.soal_id == id.soal_id).limit(1).scalar()
                db.delete(tba_del)
                db.commit()
            objects.append(soal_create)
        #Kalau data tidak memiliki soal_id dan tidak ada data kosong maka post data baru!
        else:
            id_soal = db.query(models.soalTO).filter(models.soalTO.to_id == id_dict)
            for id in id_soal:
                tba_del = db.query(models.soalTO).filter(models.soalTO.soal_id == id.soal_id).limit(1).scalar()
                db.delete(tba_del)
                db.commit()
            objects.append(soal_create)
    db.bulk_save_objects(objects)
    db.commit()
    return objects

@routers.post("/take/{to_slug}")
def take_to(to_slug: str, db: Session = Depends(get_db), current_user: int = Depends(auth.current_user)):
    current = str(current_user.user_id)
    taken_tos = db.query(models.takenTO).filter(models.takenTO.user_id == current).all()
    taken_count = []
    for taken in taken_tos:
        taken_count.append(taken)
    if len(taken_count) >= 3 and current_user.membership == "Free":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have taken the maximum limit of a free user")
    current_to = db.query(models.mainTO.to_id).filter(models.mainTO.to_slug == to_slug).scalar()
    taken_to = db.query(models.takenTO.to_id).filter(models.takenTO.to_id == current_to, models.takenTO.user_id == current).limit(1).scalar()
    user_exist = str(db.query(models.takenTO.user_id).filter(models.takenTO.user_id == current_user.user_id).limit(1).scalar())
    rand = random.randint(1, 4)
    if current_to == taken_to and user_exist == current:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"You have taken this tryout")
    to_taken = models.takenTO(user_id=current_user.user_id,to_id=current_to, type=rand)
    db.add(to_taken)
    db.commit()
    db.refresh(to_taken)
    return to_taken

@routers.post("/{to_slug}/submit")
def submit_to(to_slug: str, jawab: schemas.Jawab, db: Session = Depends(get_db), current_user: int = Depends(auth.current_user)):
    current = str(current_user.user_id)
    id_to = db.query(models.mainTO.to_id).filter(models.mainTO.to_slug == to_slug).scalar()
    id_taken = db.query(models.takenTO.taken_id).filter(models.takenTO.user_id == current_user.user_id, models.takenTO.to_id == (id_to)).limit(1).scalar()
    user_exist = str(db.query(models.takenTO.user_id).filter(models.takenTO.user_id == current_user.user_id).limit(1).scalar())
    #Checking if user exists in the taken table
    if current == user_exist and id_taken != None:
        correct = 0
        false = 0
        user_answer = models.draftTO(to_id=id_to, user_id=current_user.user_id, **jawab.dict())
        draft_content = db.query(models.draftTO).filter(models.draftTO.user_id == current_user.user_id, models.draftTO.to_id == id_to).limit(1).scalar()
        draft_user = db.query(models.draftTO.user_id).filter(models.draftTO.user_id == current_user.user_id, models.draftTO.to_id == id_to).limit(1).scalar()
        #Checking if the current user exists in the draft table
        if current == str(draft_user):
            db.delete(draft_content)
            db.commit()
            db.add(user_answer)
            db.commit()
        else:
            db.add(user_answer)
            db.commit()
            db.refresh(user_answer)
        correction = db.query(models.draftTO.user_answers).filter(models.draftTO.user_id == current, models.draftTO.to_id == id_to).scalar()
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
            if db.query(models.soalTO.correctAns).filter(models.soalTO.soal_id == ansIds[counter]).limit(1).scalar() == cor[counter]:
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
        
        finalScore = (correct / len(cor)) * 100
        final = models.hasilTO(user_id=current, to_id=id_to, taken_id=id_taken, totalCorrect=correct, totalFalse=false, score=finalScore)
        bahas = models.bahasTO(user_id=current, to_id=id_to, user_answers=pembahasan)
        #Final check if user in hasil table exists with the hasil id existing
        hasil_exist = db.query(models.hasilTO.hasil_id).filter(models.hasilTO.taken_id == id_taken).limit(1).scalar()
        to_hasil = db.query(models.hasilTO).filter(models.hasilTO.user_id == current_user.user_id, models.hasilTO.hasil_id == hasil_exist, models.hasilTO.to_id == id_to).scalar()
        if to_hasil != None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You have already submitted this tryout")
        else:
            db.add(bahas)
            db.commit()
            db.add(final)
            db.commit()
            db.refresh(final)
            return final
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User conflict - return to menu")

@routers.delete("/remove/{to_slug}")
def drop_to(to_slug: str, db: Session = Depends(get_db),current_user: int = Depends(auth.current_user)):
    taken_query = db.query(models.takenTO).filter(models.mainTO.to_slug == to_slug, models.takenTO.user_id == current_user.user_id).limit(1).scalar()
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

@routers.get("/results")
def result(db: Session = Depends(get_db), current_user: int = Depends(auth.current_user)):
    results = db.query(models.hasilTO).filter(models.hasilTO.user_id == current_user.user_id).all()
    return results

@routers.get("/check/{to_slug}")
def check(to_slug: str, db: Session = Depends(get_db), current_user: int = Depends(auth.current_user)):
    id_to = db.query(models.mainTO.to_id).filter(models.mainTO.to_slug == to_slug).scalar()
    hasil_exist = db.query(models.hasilTO.hasil_id).filter(models.hasilTO.user_id == current_user.user_id, models.hasilTO.to_id == id_to).scalar()
    user_check = db.query(models.hasilTO).filter(models.hasilTO.user_id == current_user.user_id, models.hasilTO.hasil_id == hasil_exist, models.hasilTO.to_id == id_to).scalar()

    if user_check != None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have submitted this tryout!")
    
    else:
        return ("Good luck and have fun!")
    
@routers.post("/{to_slug}/start")
def start(to_slug: str, db: Session = Depends(get_db), current_user: int = Depends(auth.current_user)):
    id_to = db.query(models.mainTO.to_id).filter(models.mainTO.to_slug == to_slug).scalar()
    to_duration = db.query(models.mainTO.duration).filter(models.mainTO.to_slug == to_slug).scalar()
    type = db.query(models.takenTO.type).filter(models.takenTO.to_id == id_to, models.takenTO.user_id == current_user.user_id).scalar()
    drafts = db.query(models.draftTO).filter(models.draftTO.to_id == id_to, models.draftTO.user_id == current_user.user_id).scalar()
    qs = []
    #tick counter and soal numbering
    counter = 0
    cids = 0
    #soal tidak diacak sama sekali
    if type == 1:
        soal = db.query(models.soalTO.soal_id).filter(models.soalTO.to_id == id_to).all()
        soal1 = db.query(models.soalTO.soal_id).filter(models.soalTO.to_id == id_to).order_by(asc(models.soalTO.soal_id)).limit(1).scalar()
        lenn = len(soal)
        while counter < lenn:
            ids = soal1 + cids
            soals = db.query(models.soalTO.soal_id).filter(models.soalTO.soal_id == ids).scalar()
            if soals != None:
                qs.append(str(soals))
                cids += 1
                counter += 1
            else:
                counter += 1
                cids = counter + 1
    #soal diacak 50/50
    elif type == 2:
        soal = db.query(models.soalTO.soal_id).filter(models.soalTO.to_id == id_to).all()
        soal1 = db.query(models.soalTO.soal_id).filter(models.soalTO.to_id == id_to).order_by(asc(models.soalTO.soal_id)).limit(1).scalar()
        lenn = len(soal)
        #total soal numbers
        snum = len(soal)
        lend = ceil(lenn / 2)
        while counter <= lenn:
            if counter < lend:
                ids = soal1 + cids
                soals = db.query(models.soalTO.soal_id).filter(models.soalTO.soal_id == ids).scalar()
                if soals != None:
                    qs.append(str(soals))
                    cids += 1
                    counter += 1
                else:
                    cids = counter + 1
                    counter += 1
            elif counter >= lend:
                ids = soal1 + snum
                soals = db.query(models.soalTO.soal_id).filter(models.soalTO.soal_id == ids).scalar()
                if soals != None:
                    qs.append(str(soals))
                    snum -= 1
                    counter += 1
                else:
                    snum -= 1
                    counter += 1
    #1/2 soal diacak, setengah awal soal dibalik dan setengah akhir soal dibalik.
    elif type == 3:
        soal = db.query(models.soalTO.soal_id).filter(models.soalTO.to_id == id_to).all()
        soal1 = db.query(models.soalTO.soal_id).filter(models.soalTO.to_id == id_to).order_by(asc(models.soalTO.soal_id)).limit(1).scalar()
        lenn = len(soal)
        #total soal numbers
        snum = len(soal)
        lend = ceil(lenn / 2)
        cids = lend
        while counter <= lenn:
            if counter <= lend:
                ids = soal1 + cids
                soals = db.query(models.soalTO.soal_id).filter(models.soalTO.soal_id == ids).scalar()
                if soals != None:
                    qs.append(str(soals))
                    cids -= 1
                    counter += 1
                else:
                    cids -= 1
                    counter += 1
            elif counter >= lend:
                ids = soal1 + snum
                soals = db.query(models.soalTO.soal_id).filter(models.soalTO.soal_id == ids).scalar()
                if soals != None:
                    qs.append(str(soals))
                    snum -= 1
                    counter += 1
                else:
                    snum -= 1
                    counter += 1
    # 100% acak
    elif type == 4:
        rando = []
        soal = db.query(models.soalTO.soal_id).filter(models.soalTO.to_id == id_to).all()
        soal1 = db.query(models.soalTO.soal_id).filter(models.soalTO.to_id == id_to).order_by(asc(models.soalTO.soal_id)).limit(1).scalar()
        lenn = len(soal)
        while counter < lenn:
            rands = choice([i for i in range(0, lenn) if i not in rando])
            rando.append(rands)
            ids = soal1 + rands
            soals = db.query(models.soalTO.soal_id).filter(models.soalTO.soal_id == ids).scalar()
            if soals != None:
                qs.append(str(soals))
                counter += 1
            else:
                counter += 1
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The specified type is invalid") 
    if drafts != None:
        return drafts
    current = current_user.user_id
    dueAt = datetime.now() + timedelta(minutes=to_duration)
    draft_create = models.draftTO(soal_struct=qs, to_id=id_to, user_id=current, duration=dueAt)
    db.add(draft_create)
    db.commit()
    db.refresh(draft_create)
    return draft_create

@routers.get("/{to_slug}/start/retrieve")
def getDraft(to_slug: str, db: Session = Depends(get_db), current_user: int = Depends(auth.current_user)):
    id_to = db.query(models.mainTO.to_id).filter(models.mainTO.to_slug == to_slug).scalar()
    drafts = db.query(models.draftTO).filter(models.draftTO.to_id == id_to, models.draftTO.user_id == current_user.user_id).scalar()
    return drafts


@routers.post("/{to_slug}/ongoing")
def ongoing(to_slug: str, answ: schemas.Draft, db: Session = Depends(get_db), current_user: int = Depends(auth.current_user)):
    id_to = db.query(models.mainTO.to_id).filter(models.mainTO.to_slug == to_slug).scalar()
    drafts = db.query(models.draftTO.draft_id).filter(models.draftTO.to_id == id_to, models.draftTO.user_id == current_user.user_id).scalar()
    draft_content = db.query(models.draftTO).filter(models.draftTO.user_id == current_user.user_id, models.draftTO.to_id == id_to).limit(1).scalar()
    soal_str = db.query(models.draftTO.soal_struct).filter(models.draftTO.user_id == current_user.user_id, models.draftTO.to_id == id_to).scalar()
    dura = db.query(models.draftTO.duration).filter(models.draftTO.to_id == id_to, models.draftTO.user_id == current_user.user_id).scalar()
    add_answers = models.draftTO(draft_id=drafts, soal_struct=soal_str, to_id=id_to, user_id=current_user.user_id, user_answers=answ.user_answers, duration=dura)
    if drafts != None:
        db.delete(draft_content)
        db.commit()
        db.add(add_answers)
        db.commit()
    else:
        db.add(add_answers)
        db.commit()
    return ("Added!")

@routers.get("/{to_slug}/pembahasan")
def pembahasan(to_slug: str, db: Session = Depends(get_db), current_user: int = Depends(auth.current_user)):
    id_to = db.query(models.mainTO.to_id).filter(models.mainTO.to_slug == to_slug).scalar()
    bahas_exist = db.query(models.bahasTO).filter(models.bahasTO.user_id == current_user.user_id, models.bahasTO.to_id == id_to).scalar()
    ids = []
    details = []
    user_ans = []
    if bahas_exist != None:
        bahas_answ = db.query(models.bahasTO.user_answers).filter(models.bahasTO.user_id == current_user.user_id, models.bahasTO.to_id == id_to).scalar()
        score_to = db.query(models.hasilTO.score).filter(models.hasilTO.to_id == id_to, models.hasilTO.user_id == current_user.user_id).scalar()
        for bhs in bahas_answ:
            ids.append(bhs['soal_id'])
            details.append(bhs['detail'])
            user_ans.append(bhs['answer'])
        payload = []
        counter = 0
        while counter < len(ids):
            list_soal = db.query(models.soalTO).filter(models.soalTO.soal_id == ids[counter]).scalar()
            if list_soal == None:
                counter += 1
            elif list_soal != None:
                data = {
                    "soal_detail": list_soal,
                    "details": details[counter],
                    "user_ans": user_ans[counter],
                    "score": score_to
                }
                payload.append(data)
                counter+=1
        return payload

    else:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="You haven't completed this tryout yet.")
    
@routers.get("/{to_slug}/peserta")
def peserta(to_slug: str, db: Session = Depends(get_db)):
    id_to = db.query(models.mainTO.to_id).filter(models.mainTO.to_slug == to_slug).scalar()
    taken_to = db.query(models.takenTO).filter(models.takenTO.to_id == id_to).all()
    users = []
    types = []
    payload = []
    counter = 0
    length = len(taken_to)
    for user in taken_to:
        user_ids = db.query(models.Users.user_id).filter(models.Users.user_id == user.user_id).scalar()
        users.append(user_ids)
    for type in taken_to:
        to_type = db.query(models.takenTO.type).filter(models.takenTO.to_id == id_to, models.takenTO.user_id == type.user_id).scalar()
        types.append(to_type)
    while counter < length:
        data = {
            "user_id": users[counter],
            "nama": db.query(models.Users.user_name).filter(models.Users.user_id == users[counter]).scalar(),
            "title": db.query(models.mainTO.to_title).filter(models.mainTO.to_id == id_to).scalar(),
            "startsAt": db.query(models.mainTO.startsAt).filter(models.mainTO.to_id == id_to).scalar(),
            "type": types[counter]
        }
        payload.append(data)
        counter+=1
    return payload