from fastapi import FastAPI, Depends, UploadFile, File
from sqlalchemy.orm import Session
from .database import engine, get_db
from .routers import to, user, bs, payment, admin
from fastapi.middleware.cors import CORSMiddleware
from . import database
import sentry_sdk

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

# sentry_sdk.init(
#     dsn="https://f34d02beeb684332aed25456ffb70f86@o4505264942284800.ingest.sentry.io/4505274290077696",

#     # Set traces_sample_rate to 1.0 to capture 100%
#     traces_sample_rate=1.0,
# )

app = FastAPI()

app.include_router(user.routers)
app.include_router(to.routers)
app.include_router(bs.routers)
app.include_router(payment.routers)
app.include_router(admin.routers)


@app.get("/")
def home(db: Session = Depends(get_db)):
    return 0
       