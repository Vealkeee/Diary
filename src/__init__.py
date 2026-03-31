__all__ = ("router")

from aiogram import Router
from src.handlers import start
from src.handlers.registration import registration

router = Router()

router.include_routers(
    start.router,
    registration.router
)