from pydantic import BaseModel
from datetime import date
from decimal import Decimal


class AllocationCreate(BaseModel):
    transfer_customer_id: int
    invoice_id: int
    amount: Decimal
    allocated_date: date


class AllocationOut(BaseModel):
    id: int
    transfer_customer_id: int
    invoice_id: int
    amount: Decimal
    allocated_date: date

    class Config:
        from_attributes = True