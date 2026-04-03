from sqlalchemy import select
from src.db.engine import localSession
from src.db.models import Student, Group

async def compareFunc(tgID):

    with localSession() as session:
        try:
            stmt1 = (
                select(Student.tgID, Student.first_name,
                    Student.second_name, Student.group_name).
                where(Student.tgID == tgID)
            )

            scalarID, first_name, second_name, group_name = session.execute(stmt1).first()

            stmt2 = (
                    select(Group.headman_name, Group.headman_second_name, Group.headman_tgID).
                    where(Group.group_name == group_name)
                )
            
            hdName, hdSecondName, hdtgID = session.execute(stmt2).first()

            first_user = ' '.join([f"{first_name}", f"{second_name}", f"{scalarID}"])
            second_user = ' '.join([f"{hdName}", f"{hdSecondName}", f"{hdtgID}"])

            if first_user == second_user:
                return True
            
        except Exception:
            return False