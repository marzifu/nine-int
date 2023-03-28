from fastapi import FastAPI, Depends, UploadFile, File
from sqlalchemy.orm import Session
from .database import engine, get_db
from .routers import to, user, materi, bs
from fastapi.middleware.cors import CORSMiddleware
from . import database
from fastapi.staticfiles import StaticFiles
from PIL import Image

database.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(user.routers)
app.include_router(to.routers)
app.include_router(bs.routers)
app.include_router(materi.routers)


@app.get("/")
def home(db: Session = Depends(get_db)):
    return 0
       