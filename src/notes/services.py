from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile
from .models import Note
from .db_models import Notes
from sqlalchemy import select, asc
from pathlib import Path
from datetime import datetime
from utils import make_folder


class NoteService:
    async def add_note(self, note_data: dict, file: UploadFile, session: AsyncSession):
        file_name = file.filename
        new_note = Notes(**note_data)
        new_note.file_name = file_name
        new_note.file_type = file.content_type
        # course_code, year = note_data["course_code"], datetime.now().year
        session.add(new_note)
        await session.commit()
        return new_note

    async def get_note_by_department(self, department: str, session: AsyncSession):
        statement = (
            select(Notes)
            .where(Notes.department == department)
            .order_by(asc(Notes.course_code))
        )
        result = await session.execute(statement)
        notes = result.scalars().all()
        return notes

    async def get_note_by_course_code(self, course_code: str, session: AsyncSession):
        statement = (
            select(Notes)
            .where(Notes.course_code == course_code)
            .order_by(asc(Notes.date_uploaded))
        )
        result = await session.execute(statement)
        notes = result.scalars().all()
        return notes

    async def get_all_notes(self, session: AsyncSession):
        statement = select(Notes).offset(10).limit(5)
        result = await session.execute(statement=statement)
        notes = result.scalars().all()
        return notes
