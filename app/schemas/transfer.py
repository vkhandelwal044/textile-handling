from pydantic import BaseModel
from typing import Optional
from datetime import date
from decimal import Decimal


class TransferCreate(BaseModel):
    stage: str
    transfer_date: date
    total_amount: Decimal
    is_lump_sum: bool = False
    sender: str
    receiver: str
    reference_note: Optional[str] = None
    evidence_type: str = "call"
    status: str = "pending"


class TransferOut(BaseModel):
    id: int
    stage: str
    transfer_date: date
    total_amount: Decimal
    is_lump_sum: bool
    sender: str
    receiver: str
    reference_note: Optional[str] = None
    evidence_type: str
    status: str

    class Config:
        from_attributes = True