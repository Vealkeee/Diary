from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Annotated

from sqlalchemy.orm import Session

from src.db.models import Grade
from src.db.engine import localSession

router = APIRouter(prefix="/college/data", tags=["✨ POST"])

subject_map = {
    "math": "математика",
    "biology": "биология",
    "russian": "русский язык",
    "informatics": "информатика",
    "physics": "физика",
    "literature": "литература",
    "history": "история",
    "english": "английский язык",
    "physic_culture": "физическая культура",
    "social_science": "обществознание",
    "opd": "ОПД"
}

async def getDB():
    db = localSession()
    try:
        yield db
    finally:
        db.close()

sessionDep = Annotated[Session, Depends(getDB)]

class Schema(BaseModel):
    student_id: int
    math: int | list[int]
    biology: int | list[int]
    russian: int| list[int]
    informatics: int| list[int]
    physics: int| list[int]
    literature: int| list[int]
    history: int| list[int]
    english: int| list[int]
    physic_culture: int| list[int]
    social_science: int| list[int]
    opd: int| list[int]

@router.post("/grades")
async def insertGrades(gradesUP: Schema, db: sessionDep):

    data = gradesUP.dict()

    for subject, value in data.items():
        if subject == "student_id":
            continue

        subject_ru = subject_map.get(subject, subject)

        if isinstance(value, list):
            for v in value:
                db.add(Grade(
                    student_id=gradesUP.student_id,
                    subject_name=subject_ru,
                    grade=v
                ))
        else:
            db.add(Grade(
                student_id=gradesUP.student_id,
                subject_name=subject_ru,
                grade=value
            ))

    db.commit()