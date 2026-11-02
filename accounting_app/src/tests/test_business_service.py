import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.base import Base
from src.models.business import Business
from src.services.business import get_active_businesses, get_business_by_id

engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    db_session = TestingSessionLocal()

    bus1 = Business(name="Business 1", invoice_prefix="B1", is_active=True)
    bus2 = Business(name="Business 2", invoice_prefix="B2", is_active=True)
    bus3 = Business(name="Archived Business", invoice_prefix="AB", is_active=False)
    db_session.add_all([bus1, bus2, bus3])
    db_session.commit()

    yield db_session
    db_session.close()
    Base.metadata.drop_all(bind=engine)

def test_get_active_businesses(db):
    active_bizes = get_active_businesses(db)
    assert len(active_bizes) == 2
    names = [b.name for b in active_bizes]
    assert "Business 1" in names
    assert "Business 2" in names
    assert "Archived Business" not in names

def test_get_business_by_id(db):
    biz = get_business_by_id(db, 1)
    assert biz is not None
    assert biz.name == "Business 1"

    missing_biz = get_business_by_id(db, 999)
    assert missing_biz is None
