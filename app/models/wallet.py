import uuid
from decimal import Decimal

from sqlalchemy import Column, Numeric, String

from app.db import Base


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    balance = Column(Numeric(18, 2), default=0, nullable=False)
