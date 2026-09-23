from pydantic import BaseModel
from typing import Optional
from datetime import date
from decimal import Decimal


class InvoiceCreate(BaseModel):
    customer_id: int
    invoice_number: str
    invoice_date: date
    total_amount: Decimal


class InvoiceOut(BaseModel):
    id: int
    customer_id: int
    invoice_number: str
    invoice_date: date
    total_amount: Decimal
    paid_amount: Decimal
    status: str

    class Config:
        from_attributes = True