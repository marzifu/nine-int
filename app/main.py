from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from . import modelsTO
from .database import engine, get_db
from .routers import to, user, materi, bs
from fastapi.middleware.cors import CORSMiddleware

modelsTO.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.routers)
app.include_router(to.routers)
app.include_router(bs.routers)
app.include_router(materi.routers)


@app.get("/")
def home(db: Session = Depends(get_db)):
    return 0
       