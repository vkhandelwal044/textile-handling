from sqlalchemy import Column, Integer, ForeignKey, Numeric, String
from app.database import Base


class TransferCustomer(Base):
    __tablename__ = "transfer_customers"

    id = Column(Integer, primary_key=True, index=True)
    transfer_id = Column(Integer, ForeignKey("transfers.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    intended_invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)
    amount = Column(Numeric(12, 2), nullable=False)
    status = Column(String, nullable=False, default="unallocated")