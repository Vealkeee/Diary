from sqlalchemy import select
from src.db.engine import localSession
from src.db.models import Student, Group

async def getGroupFunc(tgID):

    with localSession() as session:

        stmt = (
            select(Student.group_name).
            where(Student.tgID == tgID)
        )

        value = session.scalar(stmt)
        return value