from sqlalchemy import Column, Integer, String, Date, Numeric, Boolean
from app.database import Base


class Transfer(Base):
    __tablename__ = "transfers"

    id = Column(Integer, primary_key=True, index=True)
    stage = Column(String, nullable=False)  # CUSTOMER_TO_MCARGO / MCARGO_TO_ICARGO / ICARGO_TO_BUSINESS
    transfer_date = Column(Date, nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)
    is_lump_sum = Column(Boolean, nullable=False, default=False)
    sender = Column(String, nullable=False)
    receiver = Column(String, nullable=False)
    reference_note = Column(String, nullable=True)
    evidence_type = Column(String, nullable=False, default="call")  # call / screenshot / bank_receipt
    status = Column(String, nullable=False, default="pending")  # pending / confirmed