from fastapi import APIRouter, UploadFile, File, Depends, Form
from fastapi.responses import FileResponse
from .models import Note, NoteResponse
from .services import NoteService
from sqlalchemy.ext.asyncio import AsyncSession
from database.database_init import get_session
from typing import List
from utils import make_folder, add_file_to_folder
from datetime import datetime
from pathlib import Path
from dependencies.authorization import AccessTokenBearer, RoleAuthorization

router = APIRouter()
service = NoteService()
role_authorization = RoleAuthorization

BASE_DIR = Path(__file__).resolve().parent


@router.post("/upload_note")
async def upload_note(
    course_code: str = Form(...),
    uploaded_by: str = Form(...),
    description: str = Form(...),
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(AccessTokenBearer()),
):
    department = token_data["user"]["department"]
    level = token_data["user"]["level"]
    note_data = {
        "course_code": course_code,
        "level": level,
        "department": department,
        "uploaded_by": uploaded_by,
        "description": description,
    }
    try:
        new_note = await service.add_note(
            note_data=note_data, file=file, session=session
        )
        year = datetime.now().year
        new_note.file_url = (
            f"{BASE_DIR}/{course_code}/{year}/{new_note.note_id}-{new_note.file_name}"
        )
        await session.commit()
        make_folder(course_code=course_code, year=year)
        add_file_to_folder(file=file, file_name=new_note.file_url)
        return new_note
    except Exception as e:
        await session.rollback()
        print(e)


@router.get("/download_note", response_class=FileResponse)
async def download_note(
    file_name: str, token_data: dict = Depends(AccessTokenBearer())
):
    pass


@router.get("/view_notes", response_model=List[NoteResponse])
async def view_all_notes(
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(AccessTokenBearer()),
    authorized: bool = Depends(role_authorization),
):
    notes = await service.get_all_notes(session=session)
    return notes


@router.get("/view_notes/{department}", response_model=List[NoteResponse])
async def view_departmental_notes(
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(AccessTokenBearer()),
):
    department = token_data["user"]["department"]
    departmental_notes = await service.get_note_by_department(
        department=department, session=session
    )
    return departmental_notes


@router.get("/view_note/{course_code}")
async def view_course_note(
    course_code: str,
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(AccessTokenBearer()),
):
    course_notes = await service.get_note_by_course_code(
        course_code=course_code, session=session
    )
    return course_notes
