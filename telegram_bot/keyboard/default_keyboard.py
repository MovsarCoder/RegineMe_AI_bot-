from aiogram.types import BotCommand

# 🎯 Основные команды бота
start_command = BotCommand(
    command='start',
    description='🚀 Перезапустить бота / Главное меню'
)

help_command = BotCommand(
    command='information',
    description='🆘 Инструкции и часто задаваемые вопросы'
)

profile_command = BotCommand(
    command='profile',
    description='📊 Ваш профиль и статистика использования'
)

admin_command = BotCommand(
    command='admin_panel',
    description='👑 Админ-панель (только для администраторов)'
)
#
# technical_support = BotCommand(
#     command='support',
#     description='🛠️ Связь с технической поддержкой'
# )
#
# cooperation = BotCommand(
#     command='cooperation',
#     description='🤝 Варианты сотрудничества и партнерства'
# )

subscription_command = BotCommand(
    command='subscription',
    description='💎 Управление подпиской и тарифами'
)

# 📋 Список всех команд
commands = [
    start_command,
    help_command,
    profile_command,
    subscription_command,
    # technical_support,
    # cooperation,
    admin_command
]
