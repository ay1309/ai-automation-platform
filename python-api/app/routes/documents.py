import os
from fastapi import APIRouter, UploadFile, File

router = APIRouter()


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    documents_path = "/app/documents"

    os.makedirs(documents_path, exist_ok=True)

    file_location = os.path.join(
        documents_path,
        file.filename
    )

    with open(file_location, "wb") as f:
        f.write(await file.read())

    return {
        "message": "PDF uploaded successfully",
        "filename": file.filename
    }