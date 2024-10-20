from app.schemas.upload_database.DatabaseUploadResponse import DatabaseUploadResponse
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import pandas as pd


from app.core.OpenAiRequester import OpenAiRequester
from app.core.Prompt import Prompt


router = APIRouter()
from app.core.Db import Db


@router.post("/upload_csv", response_model=DatabaseUploadResponse)
async def upload_csv(table_name: str = Form(...), file: UploadFile = File(...)):

    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400, detail="Invalid file type. Only .csv files are allowed."
        )

    try:

        df = pd.read_csv(file.file)
        db = Db()
        db.create_table(table_name=table_name, df=df)
        db.insert_data(table_name=table_name, df=df)

    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to process CSV file: {str(e)}"
        )

    return DatabaseUploadResponse(
        message="CSV uploaded and converted to database successfully."
    )


@router.post("/query")
async def query(request: dict):

    try:

        db = Db()
        prompt = Prompt()

        table_name = request.get("table_name")
        table_details = db.get_table_schema(table_name=table_name)
        table_head = db.get_table_head(table_name=table_name)
        sql_query = prompt.get_db_query(
            request.get("question"), table_details, table_head
        )

        df = db.execute_query(sql_query)
        code_str = prompt.get_code_prompt(request.get("question"), df)

    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to process query: {str(e)}"
        )

    return table_details, table_head
