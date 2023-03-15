from fastapi import HTTPException, Response, status
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemasMT as schemas, modelsMT as models, auth
from sqlalchemy.dialects.postgresql import insert

routers = APIRouter(
    prefix="/materi",
    tags=['Materi']
)

@routers.get("/")
def materi_home(db: Session = Depends(get_db)):
    final = models.hasilTO
