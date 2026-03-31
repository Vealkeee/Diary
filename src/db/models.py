from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase
from sqlalchemy import BIGINT, JSON

class Base(DeclarativeBase):
    pass

class Student(Base):

    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    tgID: Mapped[int] = mapped_column(BIGINT, unique=True)
    chat_id: Mapped[int] = mapped_column(BIGINT)
    first_name: Mapped[str]
    second_name: Mapped[str]
    group_name: Mapped[str]

class Group(Base):

    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_name: Mapped[str]
    headman_name: Mapped[str]
    headman_tgID: Mapped[int] = mapped_column(BIGINT, unique=True)

class Grade(Base):

    __tablename__ = "grades"

    id: Mapped[int] = mapped_column(primary_key=True)
    tgID: Mapped[int] = mapped_column(BIGINT, unique=True)
    subject_name: Mapped[str]
    grade: Mapped[int]

class Class(Base):

    __tablename__ = "classes"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_name: Mapped[str]
    subject_list: Mapped[list[str]] = mapped_column(JSON)
    subject_list_day: Mapped[str]