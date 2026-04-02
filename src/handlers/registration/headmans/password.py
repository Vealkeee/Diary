import string
import secrets

from src.db.engine import localSession
from src.db.models import Group
from sqlalchemy import update

def generate_password(length=8):

    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for _ in range(length))

    return password