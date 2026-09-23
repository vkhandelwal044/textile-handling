from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.transfer import Transfer
from app.models.transfer_customer import TransferCustomer
from app.models.transfer_link import TransferLink
from app.schemas.transfer import TransferCreate, TransferOut
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