from fastapi import APIRouter

router = APIRouter()

student_json = [
    {
    "id": 1,
    "first_name": "Tom"
    }
]

@router.get("/student/{tgID}")
async def GetStudentByID(tgID: int):
    for student in student_json:
        if tgID == student["id"]:
            return student
