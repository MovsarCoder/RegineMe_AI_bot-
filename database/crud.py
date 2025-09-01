from datetime import datetime, timezone, timedelta
import logging
from typing import Optional, List

from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import selectinload, joinedload

from database.engine import AsyncSessionLocal
from database.models import User, Subscription, Groups, Support, Cooperation, Withdrawal

# Устанавливаем флаг чтобы и logging.info() отображался в терминале.
logging.getLogger().setLevel(logging.INFO)


class CrudUser:
    """Работа с таблицей пользователей"""

    def __init__(self):
        self.session = AsyncSessionLocal

    async def add_user(
            self,
            telegram_id: int,
            username: Optional[str],
            firstname: Optional[str],
            lastname: Optional[str],
            platform: Optional[str],
            day_count: int,
            is_active: bool,
            is_admin: bool,
            referred_by_telegram_id: Optional[int] = None
    ) -> Optional[User]:
        """
        Добавляет нового пользователя в базу.
        Если пользователь с таким telegram_id уже существует — возвращает None.
        Если передан telegram_id пригласившего — связывает пользователя с ним.
        """
        async with self.session() as session:
            try:
                # Проверяем, существует ли пользователь с таким telegram_id
                existing_user = await session.scalar(
                    select(User).where(User.telegram_id == telegram_id)
                )
                if existing_user:
                    logging.info(f"Пользователь с telegram_id={telegram_id} уже существует.")
                    return None

                # Если есть telegram_id пригласившего — ищем его
                referred_by_id = None
                if referred_by_telegram_id:
                    referrer = await session.scalar(
                        select(User).where(User.telegram_id == referred_by_telegram_id)
                    )
                    if referrer:
                        referred_by_id = referrer.id

                # Создаем нового пользователя
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    firstname=firstname,
                    lastname=lastname,
                    platform=platform or 'Telegram',
                    day_count=day_count,
                    is_active=is_active,
                    is_admin=is_admin,
                    referred_by_id=referred_by_id
                )

                session.add(user)
                await session.flush()
                await session.commit()

                logging.info(f"Пользователь успешно добавлен: {user}")
                return user

            except IntegrityError as e:
                await session.rollback()
                logging.error(f"IntegrityError при добавлении пользователя: {e}", exc_info=True)
                return None

            except Exception as ex:
                await session.rollback()
                logging.error(f"Ошибка при добавлении пользователя: {ex}", exc_info=True)
                return None

    async def check_is_admin_user(self):
        async with self.session() as session:
            try:
                stmt = select(User.telegram_id).where(User.is_admin == True)
                result = await session.execute(stmt)

                if result:
                    logging.info("Администраторы получены!")
                    admins = result.scalars().all()
                    return admins

                else:
                    logging.error('В базе нет администраторов!')
                    return None

            except Exception as e:
                logging.error(f"Ошибка при получении администратора: {e}")
                return []

    async def get_user_by_id(self, telegram_id: int):
        async with self.session() as session:
            try:
                stmt = (
                    select(User)
                    .options(
                        selectinload(User.subscriptions),
                        selectinload(User.support_request),
                        selectinload(User.cooperation_request),
                    )
                    .where(User.telegram_id == telegram_id)
                )
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()

                if user:
                    logging.info(f"Пользователь с telegram_id={telegram_id} найден.")
                else:
                    logging.error(f"Пользователь с telegram_id={telegram_id} не найден.")
                return user

            except Exception as e:
                logging.error(f"Ошибка при получении пользователя: {e}")
                return None

    async def get_all_telegram_ids(self):
        async with self.session() as session:
            try:
                stmt = select(User.telegram_id)
                result = await session.execute(stmt)
                users = result.scalars().all()
                if users:
                    logging.info("Успешно получены все пользователи!")
                    return users

                else:
                    logging.error("В базе нет ни одного пользователя!")
                    await session.rollback()
                    return False

            except SQLAlchemyError as e:
                logging.error(f"Произошла ошибка при попытке получить пользователей с базы данных: {e}", exc_info=True)
                await session.rollback()
                return False

    async def get_user_id_by_username(self, username: str):
        async with self.session() as session:
            try:
                stmt = select(User).where(User.username == username)
                get_user = await session.execute(stmt)
                result = get_user.scalar_one_or_none()
                if result:
                    return result.id

                else:
                    logging.error(f'Не удалось найти пользователя с таким {username=}!')
                    await session.rollback()
                    return False

            except Exception as e:
                logging.error(f"Ошибка при получении пользователя по username: {e}", exc_info=True)
                return False

    async def set_admin_user(self, id: str) -> bool:
        async with self.session() as session:
            try:
                stmt = select(User).where(User.id == id)
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()

                if user:
                    if user.is_admin:
                        logging.info(f"Пользователь {id=} уже является админом.")
                        return False

                    user.is_admin = True
                    await session.commit()
                    logging.info(f"Выдана админка пользователю {id=}")
                    return True

                else:
                    logging.warning(f"Пользователь с {id=} не найден.")
                    return False

            except Exception as e:
                await session.rollback()
                logging.error(f"Ошибка при выдаче админки: {e}", exc_info=True)
                return False

    async def remove_admin_user(self, id: str) -> bool:
        async with self.session() as session:
            try:
                stmt = select(User).where(User.id == id)
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()

                if user:
                    if not user.is_admin:
                        logging.info(f"Пользователь {id=} не является админом.")
                        return False

                    user.is_admin = False
                    await session.commit()
                    logging.info(f"Снята админка с пользователя {id=}")
                    return True

                else:
                    logging.warning(f"Пользователь с {id=} не найден.")
                    return False

            except Exception as e:
                await session.rollback()
                logging.error(f"Ошибка при снятии админки: {e}", exc_info=True)
                return False

    async def decrease_day_count(self, telegram_id: int):
        async with self.session() as session:
            try:
                stmt = select(User).where(User.telegram_id == telegram_id)
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()

                if user and user.day_count > 0:
                    user.day_count -= 1
                    await session.commit()
            except Exception as e:
                await session.rollback()
                logging.error(f"Ошибка при уменьшении day_count: {e}")

    async def set_default_daily_limit(self, default_day_count: int = 5) -> bool:
        async with self.session() as session:
            try:
                logging.info("▶️ Запущена задача: set_default_daily_limit")
                stmt = select(User)
                result = await session.execute(stmt)
                users = result.scalars().all()

                if not users:
                    logging.warning("❌ Не найдено ни одного пользователя.")
                    return False

                for user in users:
                    user.day_count = default_day_count

                await session.commit()
                logging.info(f"✅ Установлено {default_day_count} дневных запросов для {len(users)} пользователей.")
                return True

            except Exception as e:
                await session.rollback()
                logging.error(f"❌ Ошибка при обновлении дневных лимитов: {e}")
                return False



            except:
                pass

    async def set_days_for_user(self, user_id: str, day_count: int) -> bool:
        async with self.session() as session:
            try:
                stmt = select(User).where(User.id == user_id)  # поправь на свое поле
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()

                if not user:
                    logging.warning(f"❌ Не найден пользователь с id={user_id}.")
                    return False

                user.day_count = day_count
                await session.flush()  # фиксируем изменения перед коммитом
                await session.commit()
                logging.info(f"✅ Установлено {day_count} дневных запросов для пользователя {user_id}.")
                return True

            except Exception as e:
                await session.rollback()
                logging.error(f"❌ Ошибка при установке лимитов для пользователя {user_id}: {e}")
                return False

    async def remove_days_for_user(self, user_id: str, day_count: int) -> bool:
        async with self.session() as session:
            try:
                stmt = select(User).where(User.id == user_id)
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()

                if not user:
                    logging.warning(f"❌ Не найден пользователь с id={user_id}.")
                    return False

                # Уменьшаем day_count, но не ниже 0
                user.day_count = max(user.day_count - day_count, 0)
                await session.flush()
                await session.commit()
                logging.info(f"✅ Уменьшено day_count на {day_count} для пользователя {user_id}. Текущее значение: {user.day_count}")
                return True

            except Exception as e:
                await session.rollback()
                logging.error(f"❌ Ошибка при уменьшении лимитов для пользователя {user_id}: {e}")
                return False





            except:
                pass

    async def get_user_with_refs(self, telegram_id: int):
        async with self.session() as session:
            stmt = select(User).options(
                joinedload(User.referred_users).joinedload(User.subscriptions)
            ).where(User.telegram_id == telegram_id)
            result = await session.execute(stmt)
            user = result.scalars().first()
            return user


class CrudSubscription:
    def __init__(self):
        self.session = AsyncSessionLocal

    async def add_subscription(
            self,
            user_id: int,
            plan_name: str,
            expires_at: datetime,
            payment_id: str
    ) -> Optional[Subscription]:
        async with self.session() as session:
            try:
                now = datetime.now(timezone(timedelta(hours=3)))

                # Получаем последнюю подписку пользователя
                stmt = select(Subscription).where(Subscription.user_id == user_id).order_by(Subscription.expires_at.desc())
                result = await session.execute(stmt)
                existing = result.scalars().first()

                if existing:
                    # Продлеваем подписку
                    current_exp = existing.expires_at or now
                    if current_exp.tzinfo is None:
                        current_exp = current_exp.replace(tzinfo=timezone(timedelta(hours=3)))

                    base = max(current_exp, now)
                    delta = expires_at - now  # количество дней новой подписки
                    new_exp = base + delta

                    existing.expires_at = new_exp
                    existing.purchased_at = now
                    existing.plan_name = plan_name
                    existing.payment_id = payment_id

                    await session.commit()
                    await session.refresh(existing)
                    logging.info(f"✅ Продлена подписка: {existing}")
                    return existing

                # Создаем новую подписку
                new_sub = Subscription(
                    user_id=user_id,
                    plan_name=plan_name,
                    expires_at=expires_at,
                    payment_id=payment_id,
                    purchased_at=now
                )
                session.add(new_sub)

                user = await session.get(User, user_id)
                if user and not user.has_purchased:
                    user.has_purchased = True
                    if user.referred_by_id:
                        referrer = await session.get(User, user.referred_by_id)
                        if referrer:
                            referrer.referral_balance = (referrer.referral_balance or 0) + 50

                await session.commit()
                await session.refresh(new_sub)
                logging.info(f"✅ Создана новая подписка: {new_sub}")
                return new_sub

            except IntegrityError as e:
                await session.rollback()
                logging.error(f"❌ IntegrityError при подписке: {e}", exc_info=True)
                return None
            except Exception as e:
                await session.rollback()
                logging.error(f"❌ Ошибка при добавлении подписки: {e}", exc_info=True)
                return None

    async def remove_user_if_subscription_expired(self):
        async with self.session() as session:
            try:
                logging.info("▶️ Запущена задача: remove_user_if_subscription_expired")
                now_time = datetime.now()
                stmt = select(Subscription).where(Subscription.expires_at <= now_time)
                result = await session.execute(stmt)
                expired_subscriptions = result.scalars().all()

                for subscription in expired_subscriptions:
                    await session.delete(subscription)

                await session.commit()
                logging.info(f'Удалены пользователи и подписки с истекшим сроком: {len(expired_subscriptions)}.')
            except Exception as e:
                await session.rollback()
                logging.error(f"Ошибка при удалении пользователей: {e}", exc_info=True)


class CrudSupport:
    def __init__(self):
        self.session = AsyncSessionLocal

    async def create_request(self,
                             telegram_id: int,
                             username: str,
                             text: str):
        async with self.session() as session:
            new_request = Support(
                telegram_id=telegram_id,
                username=username,
                text_requests=text
            )
            session.add(new_request)
            await session.commit()
            await session.refresh(new_request)
            return new_request

    async def get_all_requests(self):
        async with self.session() as session:
            result = await session.execute(select(Support))
            return result.scalars().all()

    async def get_requests_by_id(self, id):
        async with self.session() as session:
            stmt = select(Support).where(Support.id == id)
            get_requests = await session.execute(stmt)
            result = get_requests.scalar_one_or_none()
            return result

    async def cancel_request(self, request_id: int) -> bool:
        async with self.session() as session:
            stmt = delete(Support).where(Support.id == request_id)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0


class CrudCooperation:
    def __init__(self):
        self.session = AsyncSessionLocal

    async def create_request(self,
                             telegram_id: int,
                             username: str,
                             text: str):
        async with self.session() as session:
            new_request = Cooperation(
                telegram_id=telegram_id,
                username=username,
                text_requests=text
            )

            session.add(new_request)
            await session.commit()
            await session.refresh(new_request)
            return new_request

    async def get_all_requests(self):
        async with self.session() as session:
            result = await session.execute(select(Cooperation))
            return result.scalars().all()

    async def get_requests_by_id(self, id):
        async with self.session() as session:
            stmt = select(Cooperation).where(Cooperation.id == id)
            get_requests = await session.execute(stmt)
            result = get_requests.scalar_one_or_none()
            return result

    async def cancel_request(self, request_id: int) -> bool:
        async with self.session() as session:
            print(1)
            stmt = delete(Cooperation).where(Cooperation.id == request_id)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0

    async def accept_request(self, request_id: int) -> bool:
        async with self.session() as session:
            print(2)
            stmt = delete(Cooperation).where(Cooperation.id == request_id)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0


class CrudGroup:
    def __init__(self):
        self.session = AsyncSessionLocal

    async def add_group(self,
                        group_name: str,
                        group_username: str,
                        ) -> Optional[Groups]:

        async with self.session() as session:
            try:
                if group_name and group_username:
                    group = Groups(group_name=group_name, group_username=group_username)
                    session.add(group)
                    await session.commit()
                    logging.info(f"Группа {group_username} добавлена.")
                    return group
                else:
                    logging.error(f"Нет данных в параметрах!")
                    return None

            except SQLAlchemyError as e:
                await session.rollback()
                logging.error(f"Ошибка при добавлении группы: {e}")
                return None

    async def get_group_by_id(self, group_id: int) -> Optional[Groups]:
        async with self.session() as session:
            result = await session.execute(select(Groups)
                                           .where(Groups.group_id == group_id))
            return result.scalar_one_or_none()

    async def remove_group(self):
        pass

    async def get_all_groups(self) -> List[Groups]:
        async with self.session() as session:
            try:
                result = await session.execute(select(Groups))
                groups = result.scalars().all()
                return groups
            except SQLAlchemyError as e:
                logging.error(f"Ошибка при получении списка групп: {e}")
                return []


class CrudWithdrawal:
    def __init__(self):
        self.session = AsyncSessionLocal

    async def create_withdrawal(self,
                                telegram_id: int,
                                username: str,
                                amount: float,
                                card_type: str,
                                card_number: str
                                ):
        async with self.session() as session:
            stmt = select(Withdrawal).where(Withdrawal.telegram_id == telegram_id)
            result = await session.execute(stmt)
            request_withdrawal = result.scalar_one_or_none()

            if request_withdrawal:
                logging.error(f"У пользователя уже есть запрос на снятия средств!")
                return False

            withdrawal = Withdrawal(
                telegram_id=telegram_id,
                username=username,
                amount=amount,
                card_type=card_type,
                card_number=card_number
            )
            session.add(withdrawal)
            await session.commit()
            return True

    async def get_all_withdrawal_requests(self):
        async with self.session() as session:
            try:
                stmt = select(Withdrawal).order_by(Withdrawal.request_created_at.desc())
                result = await session.execute(stmt)
                requests = result.scalars().all()

                if requests:
                    logging.info(f"Получено {len(requests)} заявок на снятие средств.")
                    return requests  # Вернёт [] даже если пусто — это нормально

                else:
                    logging.error(f"Нет заявок на снятия средств!")
                    return []

            except Exception as e:
                logging.error(f"Ошибка при получении заявок на вывод: {e}", exc_info=True)
                return []

    async def get_withdrawal_by_id(self, request_id: int):
        async with self.session() as session:
            result = await session.execute(
                select(Withdrawal).where(Withdrawal.id == request_id)
            )
            return result.scalar_one_or_none()

    async def accept_request(self, request_id: int):
        async with self.session() as session:
            withdrawal = await self.get_withdrawal_by_id(request_id)
            if withdrawal:
                user_id = withdrawal.telegram_id

                # Получаем пользователя в текущей сессии
                result = await session.execute(
                    select(User).where(User.telegram_id == user_id)
                )
                crud_user = result.scalar_one_or_none()

                if crud_user:
                    crud_user.referral_balance -= withdrawal.amount  # теперь изменения отслеживаются
                    logging.info(f"Списано {withdrawal.amount} с referral_balance пользователя {user_id}")

                await session.delete(withdrawal)
                await session.commit()
            return withdrawal

    async def cancel_request(self, request_id: int):
        async with self.session() as session:
            withdrawal = await self.get_withdrawal_by_id(request_id)
            if withdrawal:
                await session.delete(withdrawal)
                await session.commit()
            return withdrawal

# async def main():
#     a = await CrudWithdrawal().get_all_withdrawal_requests()
#     for i in a:
#         print(i)
#
#
# asyncio.run(main())
