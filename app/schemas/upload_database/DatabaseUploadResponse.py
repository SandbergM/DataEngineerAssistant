from pydantic import BaseModel
from fastapi import UploadFile


class DatabaseUploadResponse(BaseModel):
    message: str
