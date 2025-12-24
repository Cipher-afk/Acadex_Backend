from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse

router = APIRouter()


@router.post("/upload_note")
async def upload_note(file: UploadFile = File(...)):
    pass


@router.get("/download_note", response_class=FileResponse)
async def download_note(file_name: str):
    pass


@router.get("/view_notes")
async def view_all_notes():
    pass


@router.get("/view_notes/{department}")
async def view_departmental_notes():
    pass


@router.get("/view_note/{course_code}")
async def view_course_note():
    pass
