from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.invoice import Invoice
from app.models.customer import Customer
from app.models.transfer import Transfer
from app.models.transfer_customer import TransferCustomer
from app.schemas.invoice import InvoiceCreate, InvoiceOut

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/invoices", response_model=InvoiceOut)
def create_invoice(invoice: InvoiceCreate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == invoice.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    new_invoice = Invoice(**invoice.dict(), paid_amount=0, status="unpaid")
    db.add(new_invoice)
    db.commit()
    db.refresh(new_invoice)
    return new_invoice


@router.get("/invoices/{invoice_id}", response_model=InvoiceOut)
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.get("/invoices")
def list_invoices(db: Session = Depends(get_db)):
    invoices = db.query(Invoice).all()
    result = []
    for i in invoices:
        customer = db.query(Customer).filter(Customer.id == i.customer_id).first()
        result.append({
            "id": i.id, "invoice_number": i.invoice_number,
            "customer_id": i.customer_id, "customer_name": customer.full_name if customer else "?",
            "total_amount": i.total_amount, "paid_amount": i.paid_amount, "status": i.status
        })
    return result


@router.get("/invoices/{invoice_id}/pending-status")
def invoice_pending_status(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    outstanding = invoice.total_amount - invoice.paid_amount
    if outstanding <= 0:
        return {"invoice_id": invoice_id, "outstanding": 0, "pending_with": "Nobody — fully paid"}

    customer_id = invoice.customer_id

    paid_to_mcargo_for_this = (
        db.query(TransferCustomer).join(Transfer, Transfer.id == TransferCustomer.transfer_id)
        .filter(TransferCustomer.customer_id == customer_id, Transfer.stage == "CUSTOMER_TO_MCARGO",
                TransferCustomer.intended_invoice_id == invoice_id).all()
    )
    received_for_this = (
        db.query(TransferCustomer).join(Transfer, Transfer.id == TransferCustomer.transfer_id)
        .filter(TransferCustomer.customer_id == customer_id, Transfer.stage == "ICARGO_TO_BUSINESS",
                Transfer.status == "confirmed", TransferCustomer.intended_invoice_id == invoice_id).all()
    )

    precise = len(paid_to_mcargo_for_this) > 0 or len(received_for_this) > 0

    if precise:
        total_paid_to_mcargo = sum(s.amount for s in paid_to_mcargo_for_this)
        total_received = sum(s.amount for s in received_for_this)
        precision_note = "exact — matched to this specific invoice"
    else:
        all_mcargo = (
            db.query(TransferCustomer).join(Transfer, Transfer.id == TransferCustomer.transfer_id)
            .filter(TransferCustomer.customer_id == customer_id, Transfer.stage == "CUSTOMER_TO_MCARGO").all()
        )
        all_received = (
            db.query(TransferCustomer).join(Transfer, Transfer.id == TransferCustomer.transfer_id)
            .filter(TransferCustomer.customer_id == customer_id, Transfer.stage == "ICARGO_TO_BUSINESS",
                    Transfer.status == "confirmed").all()
        )
        total_paid_to_mcargo = sum(s.amount for s in all_mcargo)
        total_received = sum(s.amount for s in all_received)
        precision_note = "estimated — no invoice was specified at payment time, based on customer's overall activity"

    if total_paid_to_mcargo < invoice.total_amount:
        pending_with = f"Customer — has only paid Mauritius Cargo {total_paid_to_mcargo} so far"
    elif total_received < total_paid_to_mcargo:
        pending_with = f"Cargo chain — {total_paid_to_mcargo} paid but only {total_received} has reached the business"
    else:
        pending_with = "Business — money received but not yet allocated to this invoice"

    return {
        "invoice_id": invoice_id, "outstanding": outstanding,
        "paid_to_mcargo": total_paid_to_mcargo, "received_by_business": total_received,
        "pending_with": pending_with, "precision": precision_note,
    }