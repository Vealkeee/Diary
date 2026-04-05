from src.db.engine import localSession
from src.db.models import Student
from sqlalchemy import select

async def getUserID(tgID):
    with localSession() as session:
        stmt = (
            select(Student.id).
            where(Student.tgID == tgID)
        )
        value = session.scalar(stmt)
        return value