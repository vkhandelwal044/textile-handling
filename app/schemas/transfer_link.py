from pydantic import BaseModel
from decimal import Decimal


class TransferLinkCreate(BaseModel):
    earlier_transfer_id: int
    later_transfer_id: int
    amount: Decimal


class TransferLinkOut(BaseModel):
    id: int
    earlier_transfer_id: int
    later_transfer_id: int
    amount: Decimal

    class Config:
        from_attributes = True