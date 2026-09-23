from pydantic import BaseModel
from decimal import Decimal
from typing import List, Optional


class BreakupCheckResult(BaseModel):
    transfer_id: int
    transfer_total: Decimal
    breakup_total: Decimal
    mismatch: bool
    difference: Decimal


class StageCheckResult(BaseModel):
    earlier_transfer_id: int
    earlier_transfer_total: Decimal
    linked_total: Decimal
    mismatch: bool
    difference: Decimal


class AllocationCheckResult(BaseModel):
    customer_id: int
    received_total: Decimal
    allocated_total: Decimal
    unallocated_amount: Decimal
    mismatch: bool