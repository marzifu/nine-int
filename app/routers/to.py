
from fastapi import HTTPException, Response, status
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemasTO as schemas, modelsTO as models, auth
from sqlalchemy.dialects.postgresql import insert

routers = APIRouter(
    prefix="/tryouts",
    tags=['Tryout']
)

@routers.get("", response_model=List[schemas.Tryout])
def get_to(db: Session = Depends(get_db)):
    to_get = db.query(models.mainTO).all()
    return to_get

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
        soal_create = models.soalTO(to_id=id_dict, **soals.dict())
        objects.append(soal_create)
    db.bulk_save_objects(objects)
    db.commit()
    update_stmt = insert(models.soalTO).values(soal_create).on_conflict_do_update(
        index_soal = [models.soalTO.soal_id],
        set_ = {'soal_id': insert(models.soalTO).values(soal_create).excluded.soal_id}
    )
    db.bulk_save_objects(update_stmt)
    db.commit
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

@routers.post("/{to_slug}/on")
def ongoing_to(db: Session = Depends(get_db)):
    draft_post = models.draftTO

@routers.post("/{to_slug}/submit")
def submit_to(db: Session = Depends(get_db), current_user: int = Depends(auth.current_user)):
    to_submit = models.hasilTO