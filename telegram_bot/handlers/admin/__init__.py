from aiogram import Router

router = Router()

from .newsletter import router as newsletter_router
router.include_router(newsletter_router)

from .requests_cooperation import router as requests_cooperation_router
router.include_router(requests_cooperation_router)

from .requests_support import router as requests_support_router
router.include_router(requests_support_router)

from .get_user_id_by_username import router as get_user_id_router
router.include_router(get_user_id_router)

from .add_admin import router as add_admin_router
router.include_router(add_admin_router)

from .remove_admin import router as remove_admin_router
router.include_router(remove_admin_router)

from .decrease_day_limit import router as remove_days_router
router.include_router(remove_days_router)

from .set_day_limit import router as set_day_router
router.include_router(set_day_router)

from .add_group import router as add_group_router
router.include_router(add_group_router)

from .remove_group import router as remove_group_router
router.include_router(remove_group_router)

from .list_group import router as list_group_router
router.include_router(list_group_router)

from .referral_withdrawal_requests import router as withdrawal_requests_router
router.include_router(withdrawal_requests_router)