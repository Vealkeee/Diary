import logging

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from src.db.models import Student, Grade
from src.db.engine import localSession

from sqlalchemy.orm import Session

from typing import Annotated

logging.basicConfig(level=logging.INFO, filename="logs\\endpointLog.log", filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

router = APIRouter(prefix="/college/data", tags=["✨ POST"])

async def getDB():
    db = localSession()
    try:
        yield db
    finally:
        db.close()

sessionDep = Annotated[Session, Depends(getDB)]

class Schema(BaseModel):
    first_name: str = Field(max_length=14)
    second_name: str = Field(max_length=14)
    group_name: str = Field(max_length=6)
    tgID: int
    chat_id: int
    register: bool

@router.post("/student")
async def PostStudentByID(userVal: Schema, db: sessionDep):
    try:
        
        user = Student(
            first_name = userVal.first_name,
            second_name = userVal.second_name,
            group_name = userVal.group_name,
            tgID = userVal.tgID,
            chat_id = userVal.chat_id,
            register = userVal.register
        )

        userGrades = Grade(
            tgID = userVal.tgID
        )

        db.add_all([user, userGrades])
        db.commit()
        return "Success!"

    except Exception as e:
            logging.error(f"An error occured {e}")
            raise HTTPException(status_code=422, detail=f"Data didn't pass the validation... Either the server is fucked... {e}")