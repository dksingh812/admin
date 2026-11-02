import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date

from src.database.base import Base
from src.models.business import Business
from src.services.customer import create_customer, get_customers_by_business
from src.services.supplier import create_supplier, get_suppliers_by_business
from src.services.item import create_item, get_items_by_business

engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db_session = TestingSessionLocal()

    bus1 = Business(name="Test Business", invoice_prefix="TB", is_active=True)
    db_session.add(bus1)
    db_session.commit()
    db_session.refresh(bus1)

    yield db_session, bus1
    db_session.close()
    Base.metadata.drop_all(bind=engine)

def test_create_and_get_customer(db):
    db_session, bus = db

    cust_data = {
        "name": "Acme Corp",
        "code": "C001",
        "opening_balance": 25000.0,
        "opening_balance_type": "Dr",
        "opening_balance_date": date.today()
    }
    customer = create_customer(db_session, bus.id, cust_data)
    assert customer.id is not None
    assert customer.name == "Acme Corp"
    assert customer.opening_balance == 25000.0
    assert customer.opening_balance_type == "Dr"

    customers = get_customers_by_business(db_session, bus.id)
    assert len(customers) == 1

def test_create_and_get_supplier(db):
    db_session, bus = db

    sup_data = {
        "name": "Global Supplies",
        "opening_balance": 10000.0,
        "opening_balance_type": "Cr"
    }
    supplier = create_supplier(db_session, bus.id, sup_data)
    assert supplier.name == "Global Supplies"

    suppliers = get_suppliers_by_business(db_session, bus.id)
    assert len(suppliers) == 1
    assert suppliers[0].opening_balance_type == "Cr"

def test_create_and_get_items(db):
    db_session, bus = db

    prod_data = {
        "type": "Product",
        "name": "Laptop",
        "sales_price": 50000.0,
        "gst_rate": 18.0
    }
    create_item(db_session, bus.id, prod_data)

    serv_data = {
        "type": "Service",
        "name": "Consulting",
        "sales_price": 5000.0,
        "gst_rate": 18.0
    }
    create_item(db_session, bus.id, serv_data)

    all_items = get_items_by_business(db_session, bus.id)
    assert len(all_items) == 2

    products = get_items_by_business(db_session, bus.id, "Product")
    assert len(products) == 1
    assert products[0].name == "Laptop"

    services = get_items_by_business(db_session, bus.id, "Service")
    assert len(services) == 1
    assert services[0].name == "Consulting"
