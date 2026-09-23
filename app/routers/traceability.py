from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.allocation import Allocation
from app.models.transfer_customer import TransferCustomer
from app.models.transfer import Transfer
from app.models.transfer_link import TransferLink
from app.models.invoice import Invoice
from app.models.customer import Customer
from app.schemas.traceability import PaymentTrace, TraceStep

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/traceability/allocation/{allocation_id}", response_model=PaymentTrace)
def trace_payment(allocation_id: int, db: Session = Depends(get_db)):
    allocation = db.query(Allocation).filter(Allocation.id == allocation_id).first()
    if not allocation:
        raise HTTPException(status_code=404, detail="Allocation not found")

    invoice = db.query(Invoice).filter(Invoice.id == allocation.invoice_id).first()
    tc = db.query(TransferCustomer).filter(TransferCustomer.id == allocation.transfer_customer_id).first()
    customer = db.query(Customer).filter(Customer.id == tc.customer_id).first()

    chain = []
    current_transfer_id = tc.transfer_id

    while current_transfer_id is not None:
        transfer = db.query(Transfer).filter(Transfer.id == current_transfer_id).first()
        chain.append(TraceStep(
            stage=transfer.stage,
            transfer_id=transfer.id,
            amount=transfer.total_amount,
            transfer_date=transfer.transfer_date,
            sender=transfer.sender,
            receiver=transfer.receiver,
            status=transfer.status,
        ))

        earlier_links = db.query(TransferLink).filter(TransferLink.later_transfer_id == current_transfer_id).all()

        chosen_link = None
        if len(earlier_links) == 1:
            chosen_link = earlier_links[0]
        elif len(earlier_links) > 1:
            for link in earlier_links:
                matching_share = (
                    db.query(TransferCustomer)
                    .filter(
                        TransferCustomer.transfer_id == link.earlier_transfer_id,
                        TransferCustomer.customer_id == customer.id,
                    )
                    .first()
                )
                if matching_share:
                    chosen_link = link
                    break
            if chosen_link is None:
                # fallback for older data that never got a transfer_customer entry at this stage
                for link in earlier_links:
                    earlier_transfer = db.query(Transfer).filter(Transfer.id == link.earlier_transfer_id).first()
                    if earlier_transfer.sender == customer.full_name:
                        chosen_link = link
                        break

        current_transfer_id = chosen_link.earlier_transfer_id if chosen_link else None

    chain.reverse()  # earliest stage first, business last

    return PaymentTrace(
        invoice_id=invoice.id,
        invoice_number=invoice.invoice_number,
        allocation_amount=allocation.amount,
        chain=chain,
    )