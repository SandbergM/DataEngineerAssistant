from pydantic import BaseModel
import os


class Config(BaseModel):
    app_name: str = os.getenv("APP_NAME", "FastAPI Application")
