from aiogram import F, Router
from aiogram.types import CallbackQuery

router = Router()

@router.callback_query(F.data == 'remove_group_with_subscriptions')
async def add_group_function(callback: CallbackQuery):
    pass
