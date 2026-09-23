from sqlalchemy import Column, Integer, ForeignKey, Numeric
from app.database import Base


class TransferLink(Base):
    __tablename__ = "transfer_links"

    id = Column(Integer, primary_key=True, index=True)
    earlier_transfer_id = Column(Integer, ForeignKey("transfers.id"), nullable=False)
    later_transfer_id = Column(Integer, ForeignKey("transfers.id"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)