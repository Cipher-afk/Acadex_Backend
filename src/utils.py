from pathlib import Path
import os
from datetime import date
import shutil
from fastapi import UploadFile, HTTPException
from passlib.context import CryptContext

passwd_context = CryptContext(schemes=["argon2"])


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
