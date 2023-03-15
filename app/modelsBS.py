
from .database import Base
from sqlalchemy import ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import Column, Integer, String, ARRAY, Boolean, TIMESTAMP

class takenBS(Base):
    __tablename__ = "bs_taken"

    taken_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    bs_id = Column(Integer, ForeignKey("bs_main.bs_id", ondelete="CASCADE"), nullable=False)
    status = Column(Integer, server_default="1")
    type = Column(Integer)
    #1 = taken
    #2 = ongoing
    #3 = finished
    takenAt = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    finishAt = Column(TIMESTAMP(timezone=True), nullable=True)

class mainBS(Base):
    __tablename__ = "bs_main"

    bs_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    bs_title = Column(String, nullable=False)
    bs_slug = Column(String, nullable=False, unique=True)
    published = Column(Boolean, server_default="True")
    startsAt = Column(TIMESTAMP(timezone=True))
    endsAt = Column(TIMESTAMP(timezone=True))
    createdAt = Column(TIMESTAMP(timezone=True), server_default=text("now()"))

class soalBS(Base):
    __tablename__ = "bs_soal"

    soal_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    bs_id = Column(Integer, ForeignKey("bs_main.bs_id", ondelete="CASCADE"), nullable=False)
    type = Column(Integer, nullable=False)
    #4 tipe soal
    #1 = TPS
    #2 = Literasi B.Indonesia
    #3 = Literasi B.Inggris
    #4 = Penalaran Matematika
    mapel = Column(Integer, nullable=False)
    #Identifier mapel tiap soal
    content = Column(String, nullable=False)
    image_container = Column(String)
    answers = Column(ARRAY(String), nullable=False)
    correctAns = Column(String, nullable=False)
    createdAt = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updatedAt = Column(TIMESTAMP(timezone=True))

class draftBS(Base):
    __tablename__ = "bs_draft"

    draft_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    bs_id = Column(Integer, ForeignKey("bs_main.bs_id", ondelete="CASCADE"), nullable=False)
    soal_struct = Column(ARRAY(String))
    #Storage untuk struktur soal sesuai tipe
    user_answers = Column(JSONB)
    #Storage buat jawaban user

class bahasBS(Base):
    __tablename__ = "bs_bahas"

    bahas_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    soal_struct = Column(ARRAY(String))
    #Storage untuk struktur soal dari draft
    user_answers = Column(ARRAY(JSONB))
    #Storage buat jawaban user
    video_url = Column(String)

class hasilBS(Base):
    __tablename__ = "bs_hasil"

    hasil_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    bs_id = Column(Integer, ForeignKey("bs_main.bs_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    taken_id = Column(Integer, ForeignKey("to_taken.taken_id", ondelete="CASCADE"), nullable=False)
    totalCorrect = Column(Integer)
    totalFalse = Column(Integer)
    score = Column(Integer)




    

