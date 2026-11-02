from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, Text, Date
from src.database.base import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    name = Column(String, index=True, nullable=False)
    code = Column(String, index=True)
    billing_address = Column(Text)
    shipping_address = Column(Text)
    contact_number = Column(String)
    email = Column(String)
    gstin = Column(String)
    pan = Column(String)
    state = Column(String)
    state_code = Column(String)
    category = Column(String)
    opening_balance = Column(Float, default=0.0)
    opening_balance_type = Column(String) # 'Dr' or 'Cr'
    opening_balance_date = Column(Date)
    narration = Column(Text)
    credit_period = Column(Integer, default=0) # Days
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
