from sqlalchemy.orm import Session
from src.models.customer import Customer
from typing import Optional

def create_customer(db: Session, business_id: int, data: dict) -> Customer:
    data['business_id'] = business_id
    customer = Customer(**data)
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer

def get_customers_by_business(db: Session, business_id: int):
    return db.query(Customer).filter(Customer.business_id == business_id, Customer.is_active == True).all()

def update_customer(db: Session, customer_id: int, business_id: int, data: dict) -> Optional[Customer]:
    customer = db.query(Customer).filter(Customer.id == customer_id, Customer.business_id == business_id).first()
    if customer:
        for key, value in data.items():
            setattr(customer, key, value)
        db.commit()
        db.refresh(customer)
    return customer
