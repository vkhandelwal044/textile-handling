from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.transfer import Transfer
from app.models.transfer_customer import TransferCustomer
from app.models.transfer_link import TransferLink
from app.models.allocation import Allocation
from app.schemas.reconciliation import BreakupCheckResult, StageCheckResult, AllocationCheckResult

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/reconciliation/transfer/{transfer_id}/breakup-check", response_model=BreakupCheckResult)
def check_breakup(transfer_id: int, db: Session = Depends(get_db)):
    """Does this transfer's customer-wise breakup add up to its own total?"""
    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")

    shares = db.query(TransferCustomer).filter(TransferCustomer.transfer_id == transfer_id).all()
    breakup_total = sum(s.amount for s in shares)
    difference = transfer.total_amount - breakup_total

    return BreakupCheckResult(
        transfer_id=transfer_id,
        transfer_total=transfer.total_amount,
        breakup_total=breakup_total,
        mismatch=(difference != 0),
        difference=difference,
    )


@router.get("/reconciliation/transfer/{transfer_id}/stage-check", response_model=StageCheckResult)
def check_stage_transfer(transfer_id: int, db: Session = Depends(get_db)):
    """Checks whether money moved to the next stage."""

    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")

    # Stage 3 is the final destination.
    # There is no next stage to check.
    if transfer.stage == "ICARGO_TO_BUSINESS":
        return StageCheckResult(
            earlier_transfer_id=transfer_id,
            earlier_transfer_total=transfer.total_amount,
            linked_total=transfer.total_amount,
            mismatch=False,
            difference=0,
        )

    # Stage 1 and Stage 2 must be checked against their next transfer.
    links = (
        db.query(TransferLink)
        .filter(TransferLink.earlier_transfer_id == transfer_id)
        .all()
    )

    linked_total = sum(link.amount for link in links)
    difference = transfer.total_amount - linked_total

    return StageCheckResult(
        earlier_transfer_id=transfer_id,
        earlier_transfer_total=transfer.total_amount,
        linked_total=linked_total,
        mismatch=(difference != 0),
        difference=difference,
    )


@router.get("/reconciliation/customer/{customer_id}/allocation-check", response_model=AllocationCheckResult)
def check_allocation(customer_id: int, db: Session = Depends(get_db)):
    """Has all money confirmed received for this customer been allocated to invoices?"""
    # Only count money at CONFIRMED ICARGO_TO_BUSINESS transfers — money still in transit doesn't count as "received"
    shares = (
        db.query(TransferCustomer)
        .join(Transfer, Transfer.id == TransferCustomer.transfer_id)
        .filter(
            TransferCustomer.customer_id == customer_id,
            Transfer.stage == "ICARGO_TO_BUSINESS",
            Transfer.status == "confirmed",
        )
        .all()
    )
    received_total = sum(s.amount for s in shares)

    allocated_total = 0
    for s in shares:
        allocs = db.query(Allocation).filter(Allocation.transfer_customer_id == s.id).all()
        allocated_total += sum(a.amount for a in allocs)

    unallocated = received_total - allocated_total

    return AllocationCheckResult(
        customer_id=customer_id,
        received_total=received_total,
        allocated_total=allocated_total,
        unallocated_amount=unallocated,
        mismatch=(unallocated != 0),
    )