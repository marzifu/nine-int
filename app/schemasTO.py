
from datetime import datetime
from typing import Optional
from pydantic import UUID4, BaseModel, EmailStr


class Users(BaseModel):
    user_name: str
    user_email : EmailStr
    password: str

    class Config:
        orm_mode = True

class getUsers(BaseModel):
    user_id: UUID4
    user_name: str
    user_email: str
    class Config:
        orm_mode = True

class userLogin(BaseModel):
    user_email: EmailStr
    password: str
    
    class Config:
        orm_mode = True

class Tryout(BaseModel):
    to_title: str
    to_slug: str
    to_summary: str
    startsAt: datetime
    endsAt: datetime
    class Config:
        orm_mode = True

class Soal(BaseModel):
    type: int
    mapel: int
    content: str
    answers: list
    correctAns: str
    class Config:
        orm_mode = True

class getSoal(BaseModel):
    soal_id: int
    type: int
    mapel: int
    content: str
    answers: list
    class Config:
        orm_mode = True

class Taken(BaseModel):
    type: int
    class Config:
        orm_mode = True


class getAmbil(BaseModel):
    to_id: int
    status: int
    type: int

    class Config:
        orm_mode = True

class Hasil(BaseModel):
    totalCorrect: int
    totalFalse: int
    score: int

class Jawab(BaseModel):
    user_answers: list

class Draft(BaseModel):
    soal_struct: list
    user_answers: list

class Bahas(BaseModel):
    soal_struct: str
    user_answers: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[UUID4]


