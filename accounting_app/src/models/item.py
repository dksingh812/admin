from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, Text
from src.database.base import Base

class Item(Base): # Product or Service
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    type = Column(String, nullable=False) # 'Product' or 'Service'
    name = Column(String, index=True, nullable=False)
    code = Column(String, index=True)
    hsn_sac = Column(String)
    unit = Column(String)
    sales_price = Column(Float, default=0.0)
    purchase_price = Column(Float, default=0.0)
    gst_rate = Column(Float, default=0.0)
    opening_quantity = Column(Float, default=0.0)
    reorder_level = Column(Float, default=0.0)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
