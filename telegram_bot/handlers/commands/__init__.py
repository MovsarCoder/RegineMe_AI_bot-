from aiogram import Router

router = Router()

# Подключение роутера /start
from .start import router as start_router
router.include_router(start_router)

# Подключение роутера команды /subscription
from .subscription import router as subscription_router
router.include_router(subscription_router)

# Подключение роутера /cooperation
from .cooperation import router as cooperation_router
router.include_router(cooperation_router)

# Подключение роутера /profile
from .profile import router as profile_router
router.include_router(profile_router)

# Подключение роутера команды /information
from .information import router as information_router
router.include_router(information_router)

# Подключение роутера /support
from .support import router as support_router
router.include_router(support_router)

# Подключение роутера /admin_panel
from .admin_panel import router as admin_router
router.include_router(admin_router)