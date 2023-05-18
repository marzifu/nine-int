
from datetime import datetime
from typing import Optional
from pydantic import UUID4, BaseModel

class BankSoal(BaseModel):
    bs_title: str
    bs_slug: str
    bs_summary: str
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
    bs_id: int
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
    user_answers: list

class Bahas(BaseModel):
    user_answers: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[UUID4]


