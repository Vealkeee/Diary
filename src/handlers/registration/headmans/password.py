import string
import secrets

from src.db.engine import localSession
from src.db.models import Group
from sqlalchemy import update

def generate_password(tgID, length=8):

    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    
    with localSession() as session:

        stmt = (
            update(Group).
            where(Group.headman_tgID == tgID).
            values(headman_pw=password)
        )

        session.execute(stmt)
        session.commit()

    return password