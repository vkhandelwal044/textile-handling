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


# Stage 1 in one save: the hop and its "whose money" row come in one form.
# Stage, sender and receiver are not asked for: for Stage 1 they are always
# customer -> Mauritius Cargo.
class Stage1PaymentCreate(BaseModel):
    customer_id: int
    amount: Decimal
    transfer_date: date
    evidence_type: str = "call"
    status: str = "pending"
    intended_invoice_id: Optional[int] = None
    reference_note: Optional[str] = None


class Stage1PaymentOut(BaseModel):
    transfer_id: int
    transfer_customer_id: int
    customer_id: int
    customer_name: str
    amount: Decimal


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