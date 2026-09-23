from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import SessionLocal
from app.models.customer import Customer
from app.models.invoice import Invoice
from app.schemas.payment_history import CustomerHistory, InvoiceSummary

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/payment-history/customer/{customer_id}", response_model=CustomerHistory)
def customer_history(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    invoices = db.query(Invoice).filter(Invoice.customer_id == customer_id).all()
    invoice_summaries = [
        InvoiceSummary(
            id=inv.id, invoice_number=inv.invoice_number,
            total_amount=inv.total_amount, paid_amount=inv.paid_amount, status=inv.status
        )
        for inv in invoices
    ]

    total_owed = sum(inv.total_amount for inv in invoices)
    total_paid = sum(inv.paid_amount for inv in invoices)

    return CustomerHistory(
        customer_id=customer.id,
        full_name=customer.full_name,
        invoices=invoice_summaries,
        total_owed=total_owed,
        total_paid=total_paid,
        total_outstanding=total_owed - total_paid,
    )


# NEW: returns outstanding amounts for ALL customers in a single database
# query, instead of the frontend calling customer_history() once per
# customer. This is what keeps the dashboard fast as the customer list grows.
@router.get("/payment-history/all-customers")
def all_customers_outstanding(db: Session = Depends(get_db)):
    results = (
        db.query(
            Customer.id,
            Customer.full_name,
            func.coalesce(func.sum(Invoice.total_amount), 0).label("total_owed"),
            func.coalesce(func.sum(Invoice.paid_amount), 0).label("total_paid"),
        )
        .outerjoin(Invoice, Invoice.customer_id == Customer.id)
        .group_by(Customer.id, Customer.full_name)
        .all()
    )

    return [
        {
            "customer_id": r.id,
            "full_name": r.full_name,
            "total_outstanding": float(r.total_owed) - float(r.total_paid),
        }
        for r in results
    ]