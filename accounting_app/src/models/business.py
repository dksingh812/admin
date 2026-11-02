from sqlalchemy import Column, Integer, String, Boolean
from src.database.base import Base

class Business(Base):
    __tablename__ = "businesses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(String)
    gstin = Column(String, nullable=True)
    invoice_prefix = Column(String)
    is_gst_registered = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
