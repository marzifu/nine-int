
from .database import Base
from sqlalchemy import JSON, TIME, ForeignKey, column, false, text
from sqlalchemy.sql.expression import null
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY as arr
from sqlalchemy import Column, Integer, String, ARRAY, Boolean, TIMESTAMP


class Users(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, server_default=text("gen_random_uuid()"))
    user_name = Column(String, nullable=False)
    membership = Column(String, server_default="Free")
    user_email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    createdAt = Column(TIMESTAMP(timezone=True), server_default=text("now()"))

class takenTO(Base):
    __tablename__ = "to_taken"

    taken_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    to_id = Column(Integer, ForeignKey("to_main.to_id", ondelete="CASCADE"), nullable=False)
    status = Column(Integer, server_default="1")
    type = Column(Integer)
    #1 = taken
    #2 = ongoing
    #3 = finished
    takenAt = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    finishAt = Column(TIMESTAMP(timezone=True))

class mainTO(Base):
    __tablename__ = "to_main"

    to_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    to_title = Column(String, nullable=False)
    to_slug = Column(String, nullable=False, unique=True)
    to_summary = Column(String, nullable=False)
    published = Column(Boolean, server_default="True")
    startsAt = Column(TIMESTAMP(timezone=True))
    endsAt = Column(TIMESTAMP(timezone=True))
    createdAt = Column(TIMESTAMP(timezone=True), server_default=text("now()"))

class soalTO(Base):
    __tablename__ = "to_soal"

    soal_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    to_id = Column(Integer, ForeignKey("to_main.to_id", ondelete="CASCADE"), nullable=False)
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

class draftTO(Base):
    __tablename__ = "to_draft"

    draft_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    to_id = Column(Integer, ForeignKey("to_main.to_id", ondelete="CASCADE"), nullable=False)
    soal_struct = Column(ARRAY(String))
    #Storage untuk struktur soal sesuai tipe
    user_answers = Column(JSONB)
    #Storage buat jawaban user

class bahasTO(Base):
    __tablename__ = "to_bahas"

    bahas_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    soal_struct = Column(ARRAY(String))
    #Storage untuk struktur soal dari draft
    user_answers = Column(ARRAY(JSONB))
    #Storage buat jawaban user
    video_url = Column(String)

class hasilTO(Base):
    __tablename__ = "to_hasil"

    hasil_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    taken_id = Column(Integer, ForeignKey("to_taken.taken_id", ondelete="CASCADE"), nullable=False)
    totalCorrect = Column(Integer)
    totalFalse = Column(Integer)
    score = Column(Integer)




    

