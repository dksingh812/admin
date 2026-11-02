import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.base import Base
from src.models.user import User, Role
from src.utils.security import hash_password
from src.services.auth import authenticate_user

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
    db_session.commit()

    yield db_session
    db_session.close()
    Base.metadata.drop_all(bind=engine)

def test_authenticate_success(db):
    user = authenticate_user(db, "admin", "admin123")
    assert user is not None
    assert user.username == "admin"
    assert user.role.name == "Admin"

def test_authenticate_wrong_password(db):
    user = authenticate_user(db, "admin", "wrongpass")
    assert user is None

def test_authenticate_wrong_username(db):
    user = authenticate_user(db, "nonexistent", "admin123")
    assert user is None
