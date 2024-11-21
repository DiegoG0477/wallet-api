import jwt as pyjwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from dotenv import load_dotenv

load_dotenv()

def get_secret():
    return os.getenv("JWT_SECRET", "secret_key")

security = HTTPBearer()
SECRET_KEY = get_secret()
ALGORITHM = "HS256"

def create_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + timedelta(hours=24)})
    return pyjwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        token = credentials.credentials
        payload = pyjwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token ha expirado")
    except pyjwt.JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")