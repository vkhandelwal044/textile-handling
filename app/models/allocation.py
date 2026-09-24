from sqlalchemy import Column, Integer, ForeignKey, Numeric, Date
from app.database import Base


class Allocation(Base):
    __tablename__ = "allocations"

    id = Column(Integer, primary_key=True, index=True)
    transfer_customer_id = Column(Integer, ForeignKey("transfer_customers.id"), nullable=False)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    allocated_date = Column(Date, nullable=False)
    """hello"""