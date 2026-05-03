from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class WalletOperation(BaseModel):
    operation_type: str = Field(..., pattern="^(DEPOSIT|WITHDRAW)$")
    amount: Decimal = Field(..., gt=0, decimal_places=2)

    @field_validator("amount")
    @classmethod
    def validate_amount_precision(cls, v: Decimal) -> Decimal:
        if v.as_tuple().exponent < -2:
            raise ValueError("Amount must have at most 2 decimal places")
        return v


class WalletResponse(BaseModel):
    id: UUID
    balance: Decimal

    class Config:
        from_attributes = True
