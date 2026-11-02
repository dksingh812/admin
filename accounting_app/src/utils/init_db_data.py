from src.database.session import SessionLocal
from src.models.user import Role, User
from src.models.business import Business
from src.models.financial_year import FinancialYear
from src.utils.security import hash_password
from datetime import date

def init_db_data():
    db = SessionLocal()
    roles = ["Admin", "Accountant", "Staff", "Viewer"]
    for role_name in roles:
        if not db.query(Role).filter(Role.name == role_name).first():
            db.add(Role(name=role_name))
    db.commit()

    admin_role = db.query(Role).filter(Role.name == "Admin").first()
    if not db.query(User).filter(User.username == "admin").first():
        admin_user = User(username="admin", hashed_password=hash_password("admin"), role_id=admin_role.id)
        db.add(admin_user)
    db.commit()

    businesses = [
        {"name": "PARIGANTAVYA CONSULTANTS", "address": "Delhi", "invoice_prefix": "PAR", "is_gst_registered": True},
        {"name": "BERIFY & ASSOCIATES", "address": "Delhi", "invoice_prefix": "BER", "is_gst_registered": False}
    ]
    for b_data in businesses:
        if not db.query(Business).filter(Business.name == b_data["name"]).first():
            db.add(Business(**b_data))
    db.commit()

    if not db.query(FinancialYear).filter(FinancialYear.name == "2026-27").first():
        db.add(FinancialYear(name="2026-27", start_date=date(2026, 4, 1), end_date=date(2027, 3, 31)))
    db.commit()

    db.close()
    print("Database initialized with default data.")

if __name__ == "__main__":
    init_db_data()
