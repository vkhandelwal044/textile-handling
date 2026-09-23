from pydantic import BaseModel
from decimal import Decimal
from datetime import date
from typing import List, Optional


class TraceStep(BaseModel):
    stage: str
    transfer_id: int
    amount: Decimal
    transfer_date: date
    sender: str
    receiver: str
    status: str


class PaymentTrace(BaseModel):
    invoice_id: int
    invoice_number: str
    allocation_amount: Decimal
    chain: List[TraceStep]