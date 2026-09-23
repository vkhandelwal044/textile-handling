from pydantic import BaseModel
from decimal import Decimal
from typing import List


class InvoiceSummary(BaseModel):
    id: int
    invoice_number: str
    total_amount: Decimal
    paid_amount: Decimal
    status: str


class CustomerHistory(BaseModel):
    customer_id: int
    full_name: str
    invoices: List[InvoiceSummary]
    total_owed: Decimal
    total_paid: Decimal
    total_outstanding: Decimal