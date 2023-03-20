from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import engine, get_db
from .routers import to, user, materi, bs
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    'localhost:8000',
    'https://nineint-api.herokuapp.com/',
    'localhost:3000',
    'localhost'
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
       