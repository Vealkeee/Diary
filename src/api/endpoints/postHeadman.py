import logging

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from src.db.models import Group, Student
from src.db.engine import localSession

from sqlalchemy.orm import Session
from sqlalchemy import select, update

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
    headman_second_name: str = Field(max_length=14)
    headman_name: str = Field(max_length=14)
    headman_tgID: int
    headman_pw: str
    group_name: str = Field(max_length=6)

@router.post("/headman")
async def PostHeadmanByID(userVal: Schema, db: sessionDep):
    try:
        
        user = Group(
            headman_second_name = userVal.headman_second_name,
            headman_name = userVal.headman_name,
            headman_tgID = userVal.headman_tgID,
            headman_pw = userVal.headman_pw,
            group_name = userVal.group_name
        )

        stmt = (
             update(Student).
             where(Student.tgID == userVal.headman_tgID).
             values(connected=True)
        )

        db.add(user)
        db.execute(stmt)
        db.commit()
        return "Success!"

    except Exception as e:
            logging.error(f"An error occured {e}")
            raise HTTPException(status_code=422, detail=f"Data didn't pass the validation... Either the server is fucked... {e}")