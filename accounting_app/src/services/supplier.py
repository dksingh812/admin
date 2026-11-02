from sqlalchemy.orm import Session
from src.models.supplier import Supplier
from typing import Optional

def create_supplier(db: Session, business_id: int, data: dict) -> Supplier:
    data['business_id'] = business_id
    supplier = Supplier(**data)
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier

def get_suppliers_by_business(db: Session, business_id: int):
    return db.query(Supplier).filter(Supplier.business_id == business_id, Supplier.is_active == True).all()
