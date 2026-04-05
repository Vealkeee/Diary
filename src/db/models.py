from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase, relationship
from sqlalchemy import BIGINT, JSON, ForeignKey

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
    register: Mapped[bool | None] = mapped_column(nullable=True, default=None)
    connected: Mapped[bool | None] = mapped_column(nullable=True, default=None)
    grades: Mapped[list["Grade"]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan"
    )

class Group(Base):

    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_name: Mapped[str]
    headman_name: Mapped[str]
    headman_second_name: Mapped[str]
    headman_pw: Mapped[str]
    headman_tgID: Mapped[int] = mapped_column(BIGINT, unique=True)

class Grade(Base):

    __tablename__ = "grades"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    subject_name: Mapped[str | None] = mapped_column(nullable=True)
    grade: Mapped[int | list[int]] = mapped_column(JSON)
    student: Mapped["Student"] = relationship(
        back_populates="grades"
    )

class Class(Base):

    __tablename__ = "classes"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_name: Mapped[str]
    subject_list: Mapped[list[str]] = mapped_column(JSON)
    subject_list_day: Mapped[str]