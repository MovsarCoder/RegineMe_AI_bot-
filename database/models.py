from uuid import uuid4
from datetime import datetime, timedelta, timezone
from enum import Enum
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Enum as PgEnum, Numeric
from sqlalchemy.orm import relationship, backref
from .engine import Base


class PlanType(str, Enum):
    ONE_MONTH = "ONE_MONTH"
    THREE_MONTH = "THREE_MONTH"
    SIX_MONTH = "SIX_MONTH"


class User(Base):
    __tablename__ = 'users'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String, nullable=True)
    firstname = Column(String, nullable=True)
    lastname = Column(String, nullable=True)
    platform = Column(String, nullable=False, default='Telegram')
    day_count = Column(Integer, default=5, nullable=False)
    registration_date = Column(DateTime, default=lambda: datetime.now(timezone(timedelta(hours=3))))
    referred_by_id = Column(String(36), ForeignKey('users.id'), nullable=True)
    referral_balance = Column(Integer, default=0)
    has_purchased = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)

    referred_users = relationship(
        'User',
        backref=backref('referrer', remote_side=[id]),
        lazy='selectin'
    )

    withdrawal_requests = relationship("Withdrawal", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan", single_parent=True)
    support_request = relationship("Support", back_populates="user", cascade="all, delete-orphan")
    cooperation_request = relationship("Cooperation", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username={self.username}, is_admin={self.is_admin}, day_count={self.day_count}, referral_balance={self.referral_balance})>"


class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    plan_name = Column(PgEnum(PlanType), nullable=False)
    purchased_at = Column(DateTime, default=lambda: datetime.now(timezone(timedelta(hours=3))))
    expires_at = Column(DateTime, nullable=False,
                        default=lambda: datetime.now(timezone(timedelta(hours=3))) + timedelta(days=30))  # К началу подписки добавляетcя + 30 дней
    payment_id = Column(String(64), nullable=False)  # Типичная длина платежных ID

    user = relationship("User", back_populates="subscriptions")

    def __repr__(self):
        return f'{self.id}'


class Support(Base):
    __tablename__ = 'support_requests'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, ForeignKey('users.telegram_id'), nullable=False)
    username = Column(String, nullable=False)  # Убрал ForeignKey
    text_requests = Column(String, nullable=False)
    request_created_at = Column(DateTime, default=lambda: datetime.now(timezone(timedelta(hours=3))))

    user = relationship(
        "User",
        back_populates="support_request",
        foreign_keys=[telegram_id]
    )

    def __repr__(self):
        return f'{self.id} | {self.telegram_id} | {self.username} | {self.telegram_id} | {self.request_created_at}'


class Cooperation(Base):
    __tablename__ = 'cooperation_requests'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, ForeignKey('users.telegram_id'), nullable=False)
    username = Column(String, nullable=False)
    text_requests = Column(String, nullable=False)
    request_created_at = Column(DateTime, default=lambda: datetime.now(timezone(timedelta(hours=3))))

    user = relationship(
        "User",
        back_populates="cooperation_request",
        foreign_keys=[telegram_id]
    )

    def __repr__(self):
        return f'{self.id} | {self.telegram_id} | {self.username} | {self.telegram_id} | {self.request_created_at}'


class Withdrawal(Base):
    __tablename__ = "withdrawal_requests"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, ForeignKey('users.telegram_id'), nullable=False)
    username = Column(String, nullable=False)
    amount = Column(Integer, nullable=False, default=0)
    card_number = Column(String, nullable=False)
    card_type = Column(String, nullable=False)
    request_created_at = Column(DateTime, default=lambda: datetime.now(timezone(timedelta(hours=3))))

    user = relationship(
        "User",
        back_populates="withdrawal_requests",
        foreign_keys=[telegram_id]
    )

    def __repr__(self):
        return f'{self.id} | {self.telegram_id} | {self.username} | {self.amount} | {self.request_created_at}'


class Groups(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, nullable=False)
    group_name = Column(String(36), nullable=False)
    group_username = Column(String(36), nullable=False, unique=True)

    def __repr__(self):
        return f'{self.id} | {self.group_name} | {self.group_username}'
