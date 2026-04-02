__all__ = ("router")

from aiogram import Router
from src.handlers import start
from src.handlers.registration import registration
from src.handlers.registration.locationStates import backToRegister
from src.handlers.registration.headmans import newHeadman, authHeadman
from src.handlers.registration.students import authStudent
from src.handlers.HMPanel import studentConnect

router = Router()

router.include_routers(
    start.router,
    registration.router,
    backToRegister.router,
    newHeadman.router,
    authHeadman.router,
    studentConnect.router,
    authStudent.router
)