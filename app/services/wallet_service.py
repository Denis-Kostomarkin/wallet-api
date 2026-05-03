from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.wallet import Wallet


class WalletService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_wallet(self, wallet_id: UUID) -> Wallet:
        result = await self.session.execute(
            select(Wallet).where(Wallet.id == str(wallet_id))
        )
        wallet = result.scalar_one_or_none()
        if wallet is None:
            wallet = Wallet(id=str(wallet_id), balance=Decimal("0"))
            self.session.add(wallet)
            await self.session.commit()
        return wallet

    async def get_wallet(self, wallet_id: UUID) -> Wallet | None:
        result = await self.session.execute(
            select(Wallet).where(Wallet.id == str(wallet_id))
        )
        return result.scalar_one_or_none()

    async def get_wallet_with_lock(self, wallet_id: UUID) -> Wallet | None:
        # SQLite не поддерживает SELECT FOR UPDATE, но поддерживает SERIALIZABLE isolation
        # Для демонстрации используем обычный select (в SQLite один writer anyway)
        result = await self.session.execute(
            select(Wallet).where(Wallet.id == str(wallet_id))
        )
        return result.scalar_one_or_none()

    async def deposit(self, wallet_id: UUID, amount: Decimal) -> Wallet:
        wallet = await self.get_wallet_with_lock(wallet_id)
        if wallet is None:
            wallet = Wallet(id=str(wallet_id), balance=amount)
            self.session.add(wallet)
        else:
            wallet.balance += amount
        await self.session.commit()
        return wallet

    async def withdraw(self, wallet_id: UUID, amount: Decimal) -> Wallet:
        wallet = await self.get_wallet_with_lock(wallet_id)
        if wallet is None:
            raise ValueError("Wallet not found")
        if wallet.balance < amount:
            raise ValueError("Insufficient funds")
        wallet.balance -= amount
        await self.session.commit()
        return wallet
