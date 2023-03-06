from datetime import datetime, timedelta
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import UUID4
from sqlalchemy.orm import Session
from . import modelsTO as models
from .database import get_db
from . import schemasTO as schemas

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(password: str):
    return pwd_context.hash(password)

def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

#JWT Token Component

SECRET_KEY = "NqruPHs8eIXezIPmyiZJLfpRNqyLj9QlCoUhma5Aq9KOS5uWTPgAwIn3KUNdFko5"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_token(data: dict):
    to_encode = data

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    token_gen = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return token_gen

def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id: UUID4 = payload.get("user_id")
        
        if user_id is None:
            raise credentials_exception
        token_data = schemas.TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception
    
    return token_data
    
def current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials", headers={"WWW-Authenticate":"Bearer"})

    token_verify = verify_token(token, credentials_exception)
    user = db.query(models.Users).filter(models.Users.user_id == token_verify.user_id).first()
    return user