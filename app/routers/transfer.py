from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.transfer import Transfer
from app.models.transfer_customer import TransferCustomer
from app.models.transfer_link import TransferLink
from app.models.customer import Customer
from app.models.invoice import Invoice
from app.schemas.transfer import TransferCreate, TransferOut, Stage1PaymentCreate, Stage1PaymentOut
from decimal import Decimal

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/transfers", response_model=TransferOut)
def create_transfer(
    transfer: TransferCreate,
    db: Session = Depends(get_db)
):
    if transfer.total_amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    new_transfer = Transfer(**transfer.dict())

    db.add(new_transfer)
    db.commit()
    db.refresh(new_transfer)

    return new_transfer


# Stage 1 in one save: creates the hop AND its "whose money" row together.
# Either both are saved, or neither is (no half-saves).
@router.post("/stage1-payments", response_model=Stage1PaymentOut)
def create_stage1_payment(payment: Stage1PaymentCreate, db: Session = Depends(get_db)):
    # 1. All checks first, before anything is added.
    customer = db.query(Customer).filter(Customer.id == payment.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found. Nothing was saved.")
    if payment.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive. Nothing was saved.")
    if payment.intended_invoice_id is not None:
        invoice = db.query(Invoice).filter(Invoice.id == payment.intended_invoice_id).first()
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found. Nothing was saved.")
        if invoice.customer_id != customer.id:
            bill_owner = db.query(Customer).filter(Customer.id == invoice.customer_id).first()
            bill_name = bill_owner.full_name if bill_owner else f"customer ID {invoice.customer_id}"
            raise HTTPException(
                status_code=400,
                detail=f"Invoice {invoice.invoice_number} belongs to {bill_name}, not {customer.full_name}. Nothing was saved."
            )

    # 2. Add both rows, then save them with ONE commit.
    try:
        new_transfer = Transfer(
            stage="CUSTOMER_TO_MCARGO",
            transfer_date=payment.transfer_date,
            total_amount=payment.amount,
            is_lump_sum=False,
            sender="customer",
            receiver="Mauritius Cargo Person",
            reference_note=payment.reference_note,
            evidence_type=payment.evidence_type,
            status=payment.status,
        )
        db.add(new_transfer)
        db.flush()  # gives new_transfer its id, but does not save permanently yet

        new_share = TransferCustomer(
            transfer_id=new_transfer.id,
            customer_id=customer.id,
            amount=payment.amount,
            intended_invoice_id=payment.intended_invoice_id,
            status="unallocated",
        )
        db.add(new_share)

        db.commit()  # the only save: both rows together
    except Exception:
        db.rollback()  # something failed: undo both rows
        raise

    return Stage1PaymentOut(
        transfer_id=new_transfer.id,
        transfer_customer_id=new_share.id,
        customer_id=customer.id,
        customer_name=customer.full_name,
        amount=payment.amount,
    )


@router.get("/transfers/{transfer_id}", response_model=TransferOut)
def get_transfer(
    transfer_id: int,
    db: Session = Depends(get_db)
):
    transfer = db.query(Transfer).filter(
        Transfer.id == transfer_id
    ).first()

    if not transfer:
        raise HTTPException(
            status_code=404,
            detail="Transfer not found"
        )

    return transfer


@router.get("/transfers")
def list_transfers(db: Session = Depends(get_db)):
    transfers = db.query(Transfer).all()

    return [
        {
            "id": t.id,
            "stage": t.stage,
            "total_amount": t.total_amount,
            "sender": t.sender,
            "receiver": t.receiver,
            "status": t.status
        }
        for t in transfers
    ]


@router.get("/transfers/{transfer_id}/customer-shares")
def get_customer_shares(
    transfer_id: int,
    db: Session = Depends(get_db)
):
    transfer = db.query(Transfer).filter(
        Transfer.id == transfer_id
    ).first()

    if not transfer:
        raise HTTPException(
            status_code=404,
            detail="Transfer not found"
        )

    shares = db.query(TransferCustomer).filter(
        TransferCustomer.transfer_id == transfer_id
    ).all()

    return [
        {
            "id": share.id,
            "customer_id": share.customer_id,
            "amount": share.amount,
            "intended_invoice_id": share.intended_invoice_id,
            "status": share.status
        }
        for share in shares
    ]