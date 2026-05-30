import os

from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File
from fastapi import HTTPException

router = APIRouter()

DOCUMENTS_PATH = "/app/documents"


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    os.makedirs(DOCUMENTS_PATH, exist_ok=True)

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF allowed"
        )

    file_location = os.path.join(
        DOCUMENTS_PATH,
        file.filename
    )

    with open(file_location, "wb") as f:
        f.write(await file.read())

    return {
        "message": "PDF uploaded successfully",
        "filename": file.filename
    }


@router.get("/documents")
async def list_documents():

    os.makedirs(DOCUMENTS_PATH, exist_ok=True)

    files = []

    for filename in os.listdir(DOCUMENTS_PATH):

        if filename.lower().endswith(".pdf"):

            file_path = os.path.join(
                DOCUMENTS_PATH,
                filename
            )

            size_kb = round(
                os.path.getsize(file_path) / 1024,
                2
            )

            files.append({
                "name": filename,
                "size_kb": size_kb
            })

    return files

@router.delete("/documents/{filename}")
async def delete_document(filename: str):

    file_path = os.path.join(
        DOCUMENTS_PATH,
        filename
    )

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    os.remove(file_path)

    return {
        "message": "Document deleted successfully",
        "filename": filename
    }