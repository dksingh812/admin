from sqlalchemy import Column, Integer, String, Boolean, Date
from src.database.base import Base

class FinancialYear(Base):
    __tablename__ = "financial_years"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    start_date = Column(Date)
    end_date = Column(Date)
    is_locked = Column(Boolean, default=False)
