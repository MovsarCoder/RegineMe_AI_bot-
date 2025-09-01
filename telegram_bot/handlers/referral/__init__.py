from aiogram import Router

router = Router()


from .referral_system import router as referral_system_router
router.include_router(referral_system_router)

from .withdrawal_of_funds import router as withdrawal_funds_router
router.include_router(withdrawal_funds_router)