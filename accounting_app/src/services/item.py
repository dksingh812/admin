from sqlalchemy.orm import Session
from src.models.item import Item
from typing import Optional

def create_item(db: Session, business_id: int, data: dict) -> Item:
    data['business_id'] = business_id
    item = Item(**data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

def get_items_by_business(db: Session, business_id: int, item_type: str = None):
    query = db.query(Item).filter(Item.business_id == business_id, Item.is_active == True)
    if item_type:
        query = query.filter(Item.type == item_type)
    return query.all()
