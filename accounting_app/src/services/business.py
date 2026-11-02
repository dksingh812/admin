from sqlalchemy.orm import Session
from src.models.business import Business

def get_active_businesses(db: Session):
    return db.query(Business).filter(Business.is_active == True).all()

def get_business_by_id(db: Session, business_id: int):
    return db.query(Business).filter(Business.id == business_id).first()
