from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class TransferCustomerCreate(BaseModel):
    transfer_id: int
    customer_id: int
    amount: Decimal
    intended_invoice_id: Optional[int] = None


class TransferCustomerOut(BaseModel):
    id: int
    transfer_id: int
    customer_id: int
    amount: Decimal
    intended_invoice_id: Optional[int] = None
    status: str

    class Config:
        from_attributes = True