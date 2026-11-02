from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, Text, Date
from src.database.base import Base

class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    name = Column(String, index=True, nullable=False)
    contact_details = Column(String)
    address = Column(Text)
    gstin = Column(String)
    pan = Column(String)
    state = Column(String)
    opening_balance = Column(Float, default=0.0)
    opening_balance_type = Column(String) # 'Dr' or 'Cr'
    opening_balance_date = Column(Date)
    narration = Column(Text)
    is_active = Column(Boolean, default=True)
