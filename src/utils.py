from pathlib import Path
import os
from datetime import date
import shutil
from fastapi import UploadFile, HTTPException
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
import uuid
from config import settings
import logging
from fastapi.responses import JSONResponse

passwd_context = CryptContext(schemes=["argon2"])
EXPIRY_TIME = 3600
JWT_KEY = settings.JWT_KEY
JWT_ALGORITHM = settings.JWT_ALGORITHM
REFRESH_EXPIRY = timedelta(days=2)


async def create_token(
    user_data: dict, expiry: timedelta = None, refresh: bool = False
):
    payload = {}
    payload["user"] = user_data
    payload["expiry"] = (
        datetime.now()
        + (expiry if expiry is not None else timedelta(seconds=EXPIRY_TIME))
    ).timestamp()
    payload["refresh"] = refresh
    payload["jti"] = str(uuid.uuid4())
    token = jwt.encode(payload=payload, key=JWT_KEY, algorithm=JWT_ALGORITHM)
    return token


async def decode_token(jwt_token: str):
    try:
        token_data = jwt.decode(jwt=jwt_token, key=JWT_KEY, algorithms=[JWT_ALGORITHM])
        return token_data
    except Exception as e:
        logging.exception(e)
        print(e)


async def create_tokens(user_data: dict):
    access_token = await create_token(user_data=user_data)
    refresh_token = await create_token(
        user_data=user_data, expiry=REFRESH_EXPIRY, refresh=True
    )
    response = JSONResponse(
        content={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user_data": user_data,
        }
    )
    return response


def hash_password(password: str):
    passwd_hash = passwd_context.hash(password)
    return passwd_hash


def verify_password(password, password_hash):
    verified = passwd_context.verify(password, password_hash)
    if verified is None:
        raise HTTPException(status_code=403, detail="Invalid Password")
    return True


def make_folder(course_code: str, year: int):
    path = f"./notes/{course_code.capitalize()}/{year}"
    if not os.path.exists(path):
        Path(path).mkdir(parents=True, exist_ok=True)
    else:
        pass


def add_file_to_folder(file: UploadFile, file_name: str):
    with open(file_name, "wb") as new_file:
        shutil.copyfileobj(file.file, new_file)


if __name__ == "__main__":
    make_folder("csc201", 2025)
