import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.base import Base
from src.models.user import User, Role
from src.models.business import Business
from src.models.financial_year import FinancialYear
from src.utils.security import hash_password, verify_password

engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    db_session = TestingSessionLocal()

    admin_role = Role(name="Admin")
    db_session.add(admin_role)
    db_session.commit()

    admin_user = User(
        username="admin",
        hashed_password=hash_password("admin123"),
        role_id=admin_role.id
    )
    db_session.add(admin_user)

    bus1 = Business(name="PARIGANTAVYA CONSULTANTS", invoice_prefix="PAR", is_gst_registered=True)
    bus2 = Business(name="BERIFY & ASSOCIATES", invoice_prefix="BER", is_gst_registered=False)
    db_session.add_all([bus1, bus2])
    db_session.commit()

    yield db_session
    db_session.close()
    Base.metadata.drop_all(bind=engine)

def test_password_hashing():
    password = "mysecretpassword"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False

def test_user_creation(db):
    user = db.query(User).filter(User.username == "admin").first()
    assert user is not None
    assert user.role.name == "Admin"
    assert verify_password("admin123", user.hashed_password) is True

def test_business_creation(db):
    businesses = db.query(Business).all()
    assert len(businesses) == 2
    names = [b.name for b in businesses]
    assert "PARIGANTAVYA CONSULTANTS" in names
    assert "BERIFY & ASSOCIATES" in names

    gst_bus = db.query(Business).filter(Business.name == "PARIGANTAVYA CONSULTANTS").first()
    assert gst_bus.is_gst_registered is True
    assert gst_bus.invoice_prefix == "PAR"

    non_gst_bus = db.query(Business).filter(Business.name == "BERIFY & ASSOCIATES").first()
    assert non_gst_bus.is_gst_registered is False
    assert non_gst_bus.invoice_prefix == "BER"
