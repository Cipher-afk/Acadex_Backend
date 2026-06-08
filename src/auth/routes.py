from fastapi import APIRouter, status, HTTPException, Depends, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from .models import SignUpModel, LoginModel
from .service import UserService
from utils import (
    get_all_departments,
    get_courses_from_course_reg,
    get_verification_email,
    get_password_reset_email,
)
from database.database_init import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile, File, Form
import logging
from utils import (
    create_tokens,
    create_token,
    create_safe_token,
    decode_safe_token,
    hash_password,
)
from mail import mail, create_message
from config import settings as s
from dependencies.authorization import AccessTokenBearer, RefreshTokenBearer
from typing import Dict
from datetime import datetime
from dependencies.redis_db import add_to_blacklist

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("error.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)
router = APIRouter()
service = UserService()
UNIVERSITY = "Federal University Of Otueke"
jinja = Jinja2Templates(directory="templates")
HOME_LINK = f"{s.DOMAIN_NAME}/docs"


@router.get("/add_university")
async def add_university(session: AsyncSession = Depends(get_session)):
    university = await service.add_university(
        university=str(UNIVERSITY), session=session
    )
    return university


@router.get("/add_faculties")
async def add_faculties(session: AsyncSession = Depends(get_session)):
    faculties = list(faculties for faculties in get_all_departments(UNIVERSITY))
    new_faculties = await service.add_faculties(
        faculties=faculties, university_name=UNIVERSITY, session=session
    )
    return new_faculties


@router.get("/add_departments")
async def add_departments(session: AsyncSession = Depends(get_session)):
    faculties = list(faculties for faculties in get_all_departments(UNIVERSITY))
    departments_list = [
        get_all_departments(UNIVERSITY)[faculty] for faculty in faculties
    ]
    all_departments = []
    for i in range(len(faculties)):
        departments = await service.add_departments(
            university_name=UNIVERSITY,
            departments=departments_list[i],
            faculty_name=faculties[i],
            session=session,
        )
        all_departments.append(departments)
    return all_departments


@router.get("/universities")
async def get_university(session: AsyncSession = Depends(get_session)):
    universities = await service.get_all_universities(session=session)
    return universities


@router.get("/university_faculties/{university_id}")
async def get_faculties(
    university_id: int, session: AsyncSession = Depends(get_session)
):
    faculties = await service.get_university_faculties(
        university_id=university_id, session=session
    )
    return faculties


@router.get("/faculty_departments/{faculty_id}")
async def get_departments(
    faculty_id: int, session: AsyncSession = Depends(get_session)
):
    departments = await service.get_faculty_departments(
        faculty_id=faculty_id, session=session
    )
    return departments


@router.post("/signup")
async def create_user(
    bg: BackgroundTasks,
    email: str = Form(...),
    matric_number: str = Form(..., pattern=r"[A-Z]{3}/\d{2}/[A-Z]{3}/\d{5}"),
    username: str = Form(...),
    level: int = Form(...),
    password: str = Form(...),
    university_name: str = Form(default="Federal University Of Otueke"),
    faculty_name: str = Form(...),
    department_name: str = Form(...),
    course_reg_bytes: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
):
    try:
        if level not in list(range(100, 800)):
            raise HTTPException(status_code=403, detail="Level not valid")
        signup_model = SignUpModel(
            email=email,
            matric_number=matric_number,
            username=username,
            level=level,
            password=password,
            university_name=university_name,
            faculty_name=faculty_name,
            department_name=department_name,
        )
        user, courses = await service.create_user(
            signup_model=signup_model,
            course_reg_contents=await course_reg_bytes.read(),
            session=session,
        )
        if user is not None and courses is not None:
            safe_token = await create_safe_token({"email": user.email})
            link = f"{s.DOMAIN_NAME}/verify_email/{safe_token}"
            email_html_message = get_verification_email(name=user.username, link=link)
            message = await create_message(
                recipients=[user.email],
                subject="Email Verification",
                body=email_html_message,
            )
            bg.add_task(mail.send_message, message)
        return JSONResponse(
            content={
                "Message": f"Verification email sent successfully to {user.email}",
                "Resolution": f"Please Check your email to verify your account".title(),
            }
        )
    except Exception as e:
        await session.rollback()
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add_courses")
async def add_courses(
    faculty_name: str = Form(...),
    department_name: str = Form(...),
    level: int = Form(...),
    session: AsyncSession = Depends(get_session),
    course: UploadFile = File(...),
):
    course_data = get_courses_from_course_reg(pdf_contents=await course.read())
    courses = await service.add_courses(
        courses_data=course_data,
        faculty_name=faculty_name,
        department_name=department_name,
        level=level,
        session=session,
    )
    return courses


@router.post("/login")
async def sign_in(
    login_data: LoginModel,
    bg: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    user = await service.login(login_data=login_data, session=session)
    user_data = {
        "email": user.email,
        "matric_number": user.matric_number,
        "level": user.level,
        "university_id": user.university_id,
        "faculty_id": user.faculty_id,
        "department_id": user.department_id,
    }
    if user.is_verified is False:
        safe_token = await create_safe_token({"email": user.email})
        link = f"{s.DOMAIN_NAME}/auth/verify_email/{safe_token}"
        email_html_message = get_verification_email(name=user.username, link=link)
        message = await create_message(
            recipients=[user.email],
            subject="Email Verification",
            body=email_html_message,
        )
        bg.add_task(mail.send_message, message)
        return JSONResponse(
            content={
                "Message": f"Verification email sent successfully to {user.email}",
                "Resolution": f"Please Check your email to verify your account".title(),
            }
        )
    response = await create_tokens(user_data=user_data)
    return response


@router.get("/verify_email/{token}", include_in_schema=False)
async def verify_email(
    token: str, request: Request, session: AsyncSession = Depends(get_session)
):
    token_data = await decode_safe_token(token)
    email = token_data["email"]
    home_link = HOME_LINK
    user = await service.get_user_by_email(email=email, session=session)
    await service.update_user(user=user, info={"is_verified": True}, session=session)
    return jinja.TemplateResponse(
        request=request,
        name="email_verification.html",
        context={
            "request": request,
            "username": user.username,
            "home_link": home_link,
        },  # If request is not passed it won't be able to get the static files
    )


@router.post("/request_password_reset")
async def request_password_reset(
    email: str, bg: BackgroundTasks, session: AsyncSession = Depends(get_session)
):
    user = await service.get_user_by_email(email=email, session=session)
    if user is None:
        raise HTTPException(status_code=404, detail="User Not Found")
    safe_token = await create_safe_token(user_data={"email": user.email})
    link = f"{s.DOMAIN_NAME}/auth/password_reset/{safe_token}"
    password_reset_html = get_password_reset_email(name=user.username, link=link)
    message = await create_message(
        recipients=[email],
        subject="Confirmation for password reset".title(),
        body=password_reset_html,
    )
    bg.add_task(mail.send_message, message)
    return JSONResponse(
        content={
            "Message": "Password Reset Email sent successfully".title(),
            "Resolution": "Check your email to reset your password".title(),
        }
    )


@router.get("/password_reset/{token}")
async def reset_password(
    request: Request, token: str, session: AsyncSession = Depends(get_session)
):
    token_data = await decode_safe_token(token=token)
    if token_data is None:
        raise HTTPException(status_code=403, detail="Invalid Token")
    email = token_data["email"]
    user = await service.get_user_by_email(email=email, session=session)
    if user is not None:
        return jinja.TemplateResponse(
            request=request,
            name="password_reset_form.html",
            context={"request": request, "token": token},
        )


@router.post("/password_reset")
async def verify_reset_password(
    request: Request,
    token: str,
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    token_data = await decode_safe_token(token=token)
    if token_data is None:
        raise HTTPException(status_code=403, detail="Invalid Token")
    if new_password != confirm_password:
        raise HTTPException(
            status_code=403, detail="Password doesn't match try again".title()
        )
    user = await service.get_user_by_email(email=token_data["email"], session=session)
    new_password_hash = hash_password(new_password)
    await service.update_user(
        user=user, info={"password_hash": new_password_hash}, session=session
    )
    return jinja.TemplateResponse(
        request=request,
        name="password_reset_verified.html",
        context={"request": request, "home_link": HOME_LINK},
    )


@router.get("/me")
async def get_current_user(
    token_data: Dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_session),
):
    email = token_data["user"]["email"]
    user = await service.get_user_by_email(email=email, session=session)
    return user


@router.get("/refresh")
async def get_new_access_token(token_data: Dict = Depends(RefreshTokenBearer())):
    expiry = token_data["expiry"]
    if expiry > datetime.now().timestamp():
        access_token = await create_token(user_data=token_data["user"])
        return JSONResponse(content={"Access_Token": access_token})
    raise HTTPException(status_code=403, detail="Refresh Token Expired")


@router.get("/logout")
async def logout(token_data: Dict = Depends(AccessTokenBearer())):
    jti = token_data["jti"]
    await add_to_blacklist(jti=jti)
