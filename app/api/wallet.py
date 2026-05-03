from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.schemas.wallet import WalletOperation, WalletResponse
from app.services.wallet_service import WalletService

router = APIRouter(prefix="/api/v1/wallets", tags=["wallets"])


@router.post("/{wallet_uuid}/operation", response_model=WalletResponse)
async def wallet_operation(
    wallet_uuid: UUID,
    operation: WalletOperation,
    db: AsyncSession = Depends(get_db),
):
    service = WalletService(db)
    try:
        if operation.operation_type == "DEPOSIT":
            wallet = await service.deposit(wallet_uuid, operation.amount)
        else:
            wallet = await service.withdraw(wallet_uuid, operation.amount)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return wallet


@router.get("/{wallet_uuid}", response_model=WalletResponse)
async def get_wallet(
    wallet_uuid: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = WalletService(db)
    wallet = await service.get_wallet(wallet_uuid)
    if wallet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
    return wallet
