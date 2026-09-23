from pydantic import BaseModel
from typing import Optional


class CustomerCreate(BaseModel):
    full_name: str
    mobile: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class CustomerOut(BaseModel):
    id: int
    full_name: str
    mobile: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True