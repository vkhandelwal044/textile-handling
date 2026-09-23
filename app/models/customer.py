from sqlalchemy import Column, Integer, String
from app.database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    mobile = Column(String, nullable=True)
    address = Column(String, nullable=True)
    notes = Column(String, nullable=True)