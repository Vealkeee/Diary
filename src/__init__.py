__all__ = ("router")

from aiogram import Router
from src.handlers import start

router = Router()

router.include_router(
    start.router
)