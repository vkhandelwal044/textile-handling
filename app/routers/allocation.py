from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.allocation import Allocation
from app.models.transfer_customer import TransferCustomer
from app.models.transfer import Transfer
from app.models.invoice import Invoice
from app.schemas.allocation import AllocationCreate, AllocationOut

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/allocations", response_model=AllocationOut)
def create_allocation(alloc: AllocationCreate, db: Session = Depends(get_db)):
    tc = db.query(TransferCustomer).filter(TransferCustomer.id == alloc.transfer_customer_id).first()
    if not tc:
        raise HTTPException(status_code=404, detail="Transfer customer entry not found")

    transfer = db.query(Transfer).filter(Transfer.id == tc.transfer_id).first()
    if transfer.stage != "ICARGO_TO_BUSINESS" or transfer.status != "confirmed":
        raise HTTPException(
            status_code=400,
            detail="Only confirmed India Cargo → Business transfers can be allocated to invoices"
        )

    invoice = db.query(Invoice).filter(Invoice.id == alloc.invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    already_allocated = db.query(Allocation).filter(
        Allocation.transfer_customer_id == tc.id
    ).with_entities(Allocation.amount).all()
    used_so_far = sum(a[0] for a in already_allocated)
    if used_so_far + alloc.amount > tc.amount:
        raise HTTPException(status_code=400, detail="Amount exceeds this customer's unallocated balance")

    remaining_on_invoice = invoice.total_amount - invoice.paid_amount
    if alloc.amount > remaining_on_invoice:
        raise HTTPException(status_code=400, detail="Amount exceeds invoice's remaining balance")

    new_alloc = Allocation(**alloc.dict())
    db.add(new_alloc)

    invoice.paid_amount += alloc.amount
    invoice.status = "paid" if invoice.paid_amount >= invoice.total_amount else "partially_paid"

    db.commit()
    db.refresh(new_alloc)
    return new_alloc


@router.get("/allocations/{allocation_id}", response_model=AllocationOut)
def get_allocation(allocation_id: int, db: Session = Depends(get_db)):
    alloc = db.query(Allocation).filter(Allocation.id == allocation_id).first()
    if not alloc:
        raise HTTPException(status_code=404, detail="Not found")
    return alloc