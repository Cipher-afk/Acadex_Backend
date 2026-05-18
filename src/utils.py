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
import json
from typing import List, Dict
from pprint import pprint
import fitz, pytesseract
from PIL import Image
import io
import re
from typing import Optional
import logging
from itsdangerous import URLSafeTimedSerializer

logger = logging.getLogger(__name__)

passwd_context = CryptContext(schemes=["argon2"])
EXPIRY_TIME = 3600
JWT_KEY = settings.JWT_KEY
JWT_ALGORITHM = settings.JWT_ALGORITHM
REFRESH_EXPIRY = timedelta(days=2)
serializer = URLSafeTimedSerializer(
    secret_key=settings.JWT_KEY, salt="email_verification"
)


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


async def create_safe_token(user_data: Dict):
    token = serializer.dumps(user_data, salt="email_verification")
    return token


async def decode_safe_token(token: str):
    try:
        user_data = serializer.loads(token, max_age=1800, salt="email_verification")
        return user_data
    except Exception as e:
        logging.info(e)
        return None


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


def get_all_departments(school: str) -> List[Dict]:
    with open("./departments.json", "r") as f:
        departments = json.loads(f.read())
        return departments.get(school, [])


pattern = re.compile(r"([A-Z]+\d{3})\s+([A-Z\s]+)\s+(\d+)")
# ([A-Z]+\d{3})\s+\s+(\d+)$


def get_courses_from_course_reg(
    pdf_file_path: Optional[str] = None, pdf_contents: Optional[bytes] = None
):
    doc = fitz.open(stream=pdf_contents, filetype="pdf")
    all_text = ""
    for page_num, page in enumerate(doc):
        text = page.get_text()
        if len(text.strip()) < 20:
            pix = page.get_pixmap(dpi=300)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            text = pytesseract.image_to_string(img)
        all_text += text
    all_text = all_text.replace("\n", " ")
    courses_dict = {"course_code": [], "course_title": [], "credit_unit": []}
    course_code, course_title, credit_unit = (
        courses_dict["course_code"],
        courses_dict["course_title"],
        courses_dict["credit_unit"],
    )
    for match in pattern.finditer(all_text):
        course_code.append(match.group(1))
        course_title.append(match.group(2))
        credit_unit.append(match.group(3))
    logger.info(courses_dict)
    return courses_dict


def get_verification_email(name: str, link: str):
    with open("./acadex-welcome-email.html", encoding="utf-8") as file:
        contents = file.read()
        contents = contents.replace("{Name}", name).replace("{VERIFICATION_LINK}", link)
        return contents


def get_password_reset_email(name: str, link: str):
    with open("./acadex-password-reset-email.html", encoding="utf-8") as file:
        contents = file.read()
        contents = contents.replace("{Name}", name).replace("{RESET_LINK}", link)
        return contents


if __name__ == "__main__":
    pdf_path = "./300_level_1st Semester_courses.pdf"
    get_courses_from_course_reg(pdf_file_path=pdf_path)
