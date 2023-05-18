
from datetime import datetime
from typing import List, Optional
from pydantic import UUID4, BaseModel, EmailStr


class Users(BaseModel):
    user_name: str
    user_email: EmailStr
    password: str
    phone: str

    class Config:
        orm_mode = True

class Admin(BaseModel):
    admin_name: str
    admin_email: str
    password: str
    phone: str

    class Config:
        orm_mode = True

class UpdateUser(BaseModel):
    user_id: UUID4
    user_name: str
    user_email: EmailStr
    phone: str
    address: str
    pp_link: str
    gender: str

class getUsers(BaseModel):
    user_id: UUID4
    user_name: str
    user_email: str
    address: Optional[str] = None
    gender: Optional[str] = None
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
    duration: int
    startsAt: datetime
    endsAt: datetime
    class Config:
        orm_mode = True

class Soal(BaseModel):
    soal_id: Optional[int] = None
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

class Answers(BaseModel):
    soal_id: int
    answer: str
class Jawab(BaseModel):
    user_answers: List[Answers]

class Draft(BaseModel):
    user_answers: Optional[list]

class Bahas(BaseModel):
    soal_struct: str
    user_answers: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[UUID4]



