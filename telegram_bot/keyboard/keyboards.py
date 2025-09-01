# Выбор направления улучшения качества
select_type_improvement_graphics = [
    ("🖼️ Улучшить фото — повышение резкости и детализации"),
    ("🎬 Улучшить видео — стабилизация и повышение качества"),
    ("💎 Подписка — доступ к PRO-функциям"),
    ("🛠 Техническая поддержка — вопросы и проблемы"),
    ("🤝 Сотрудничество — партнерские программы и предложения"),
]

back_photo = [
    ("⏪ Отмена", "cancel_photo")
]

back_video = [
    ("⏪ Отмена", "cancel_video")
]

cancel_cooperation = [
    ("⏪ Отмена", 'cancel_cooperation')
]

cancel_support = [
    ("⏪ Отмена", 'cancel_support')
]

cancel_newsletter = [
    ("⏪ Отмена", 'cancel_newsletter')
]

referral_system = [
    ("🎁 Реферальная система", "referral_system"),
]

referral_menu_keyboard = [
    ("💸 Вывести средства", "referral_withdraw"),
]

# Админская часть
admin_keyboard = [
    ("📬 Создать рассылку", "broadcast_message"),
    ("🧑‍💼 Сотрудничество: новые заявки", "show_requests_cooperation"),
    ("🧾 Поддержка: входящие запросы", "show_requests_support"),
    ("🔍 Найти ID пользователя по username", "get_user_id_by_username"),
    ("🛡️ Назначить администратора", "add_admin"),
    ("🚫 Убрать права администратора", "remove_admin"),
    ("❌ Уменьшить дневной лимит", "decrease_day_limit"),
    ("✅ Установить дневной лимит", "set_day_limit"),
    ("➕ Добавить группу в подписку", "add_group_to_subscription"),
    ("➖ Удалить группу с подписок", "remove_group_with_subscriptions"),
    ("📋 Список групп", "list_group"),
    ("💸 Запросы на вывод (рефералы)", "referral_withdrawal_requests"),
    ("🤖 Активность пользователей бота", "bot_user_activity"),
]


def get_accept_cancel_buttons(request_id: int):
    return [
        ("❌ Отклонить", f"cancel_cooperation_requests_{request_id}"),
        ("✅ Одобрить", f"accepted_cooperation_requests_{request_id}"),
        ("⏪ Отмена", "show_requests_cooperation_2")
    ]


def get_withdrawal_action_buttons(request_id: int):
    return [
        ("❌ Отклонить", f"cancel_withdrawal_request_{request_id}"),
        ("✅ Одобрить", f"accept_withdrawal_request_{request_id}"),
        ("⏪ Отмена", "referral_withdrawal_requests")
    ]


def get_cancel_support_buttons(request_id: int):
    return [
        ("❌ Удалить запрос", f"deleted_support_requests_{request_id}"),
        ("⏪ Отмена", "show_requests_support_2")
    ]


def subscription_keyboard(prices):
    return [
        (f'🔔 {value["label"]}', plan.name) for plan, value in prices.items()
    ]
