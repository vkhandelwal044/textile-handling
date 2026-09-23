from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.transfer_customer import TransferCustomer
from app.models.transfer import Transfer
from app.models.customer import Customer
from app.schemas.transfer_customer import TransferCustomerCreate, TransferCustomerOut
from decimal import Decimal

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/transfer-customers", response_model=TransferCustomerOut)
def create_transfer_customer(tc: TransferCustomerCreate, db: Session = Depends(get_db)):
    transfer = db.query(Transfer).filter(Transfer.id == tc.transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")
    customer = db.query(Customer).filter(Customer.id == tc.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    if tc.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    # NEW: don't let a transfer's assigned customer shares exceed its total.
    # This is what stops two separate customer breakdowns from silently
    # "double-booking" the same transfer.
    existing_total = db.query(TransferCustomer).filter(
        TransferCustomer.transfer_id == tc.transfer_id
    ).with_entities(TransferCustomer.amount).all()
    already_assigned = sum((row.amount for row in existing_total), Decimal(0))
    if already_assigned + tc.amount > transfer.total_amount:
        raise HTTPException(
            status_code=400,
            detail=f"This would assign ₹{already_assigned + tc.amount} to a transfer of only ₹{transfer.total_amount}."
        )

    new_tc = TransferCustomer(**tc.dict(), status="unallocated")
    db.add(new_tc)
    db.commit()
    db.refresh(new_tc)
    return new_tc


@router.get("/transfer-customers/{tc_id}", response_model=TransferCustomerOut)
def get_transfer_customer(tc_id: int, db: Session = Depends(get_db)):
    tc = db.query(TransferCustomer).filter(TransferCustomer.id == tc_id).first()
    if not tc:
        raise HTTPException(status_code=404, detail="Not found")
    return tc


@router.get("/transfer-customers")
def list_transfer_customers(db: Session = Depends(get_db)):
    tcs = db.query(TransferCustomer).all()
    result = []
    for tc in tcs:
        customer = db.query(Customer).filter(Customer.id == tc.customer_id).first()
        result.append({
            "id": tc.id, "transfer_id": tc.transfer_id,
            "customer_id": tc.customer_id, "customer_name": customer.full_name if customer else "?",
            "amount": tc.amount, "intended_invoice_id": tc.intended_invoice_id, "status": tc.status
        })
    return result