from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.transfer_link import TransferLink
from app.models.transfer import Transfer
from app.schemas.transfer_link import TransferLinkCreate, TransferLinkOut
from decimal import Decimal

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/transfer-links", response_model=TransferLinkOut)
def create_transfer_link(
    link: TransferLinkCreate,
    db: Session = Depends(get_db)
):
    earlier = (
        db.query(Transfer)
        .filter(Transfer.id == link.earlier_transfer_id)
        .first()
    )
    if not earlier:
        raise HTTPException(
            status_code=404,
            detail="Earlier transfer not found"
        )

    later = (
        db.query(Transfer)
        .filter(Transfer.id == link.later_transfer_id)
        .first()
    )
    if not later:
        raise HTTPException(
            status_code=404,
            detail="Later transfer not found"
        )

    if earlier.id == later.id:
        raise HTTPException(
            status_code=400,
            detail="A transfer cannot be linked to itself."
        )

    if link.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Amount must be positive"
        )

    valid_next_stage = {
        "CUSTOMER_TO_MCARGO": "MCARGO_TO_ICARGO",
        "MCARGO_TO_ICARGO": "ICARGO_TO_BUSINESS",
    }

    expected_stage = valid_next_stage.get(earlier.stage)

    if expected_stage != later.stage:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid stage connection. "
                f"{earlier.stage} can only connect to {expected_stage}."
            )
        )

    # An earlier transfer has a finite amount.
    # All outgoing links together can never consume more than it contains.
    outgoing_rows = (
        db.query(TransferLink.amount)
        .filter(
            TransferLink.earlier_transfer_id ==
            link.earlier_transfer_id
        )
        .all()
    )

    already_sent = sum(
        (row.amount for row in outgoing_rows),
        Decimal("0")
    )

    remaining = earlier.total_amount - already_sent

    if link.amount > remaining:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Only ₹{remaining} remains available from "
                f"transfer {earlier.id}. "
                f"Cannot transfer ₹{link.amount} again."
            )
        )

    # A later transfer also has a finite total.
    # Incoming links can never exceed that later transfer's total.
    incoming_rows = (
        db.query(TransferLink.amount)
        .filter(
            TransferLink.later_transfer_id ==
            link.later_transfer_id
        )
        .all()
    )

    already_received = sum(
        (row.amount for row in incoming_rows),
        Decimal("0")
    )

    later_remaining = later.total_amount - already_received

    if link.amount > later_remaining:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Only ₹{later_remaining} of transfer {later.id} "
                f"can still be linked from earlier transfers."
            )
        )

    new_link = TransferLink(**link.dict())
    db.add(new_link)
    db.commit()
    db.refresh(new_link)

    return new_link


@router.get("/transfer-links", response_model=list[TransferLinkOut])
def list_transfer_links(db: Session = Depends(get_db)):
    return db.query(TransferLink).all()


@router.get("/transfer-links/{link_id}", response_model=TransferLinkOut)
def get_transfer_link(
    link_id: int,
    db: Session = Depends(get_db)
):
    link = (
        db.query(TransferLink)
        .filter(TransferLink.id == link_id)
        .first()
    )

    if not link:
        raise HTTPException(
            status_code=404,
            detail="Not found"
        )

    return link
