from aiogram import Router

router = Router()



# Подключение всех функций связанные с коммандами
from .commands import router as commands_router
router.include_router(commands_router)


# Подключение всех функций администраторской панели
from .admin import router as admin_commands_router
router.include_router(admin_commands_router)


# Подключение роутера связанный с реферальной системой
from .referral import router as referral_router
router.include_router(referral_router)


# Подключение роутера получения фотография
from .photo.photo_handler import router as photo_router
router.include_router(photo_router)

# Подключение роутера получения Видео
from .video.video_handler import router as video_router
router.include_router(video_router)

