from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from . import modelsTO
from .database import engine, get_db
from .routers import to, user

modelsTO.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(to.routers)
app.include_router(user.routers)

@app.get("/")
def home(db: Session = Depends(get_db)):
    return 0
#@app.post("/submit")
#def submit_to(submits: submitTO):
#    correct = 0
#    false = 0
#    cursor.execute("""SELECT soal_id, "correctAns" from tryout_soal""")
#    id_verify = cursor.fetchall()
#    for row in id_verify: 
#        if submits.soal_id == row[0] and submits.user_answer == row[1]:
#            correct += 1
#        else:
#            false += 1
#    print(correct)
#    print(false)
       