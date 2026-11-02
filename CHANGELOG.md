# Changelog

## [Unreleased]
### Added
- **Phase 2 Implementation:**
  - `Customer`, `Supplier`, and `Item` models added to database schema.
  - Alembic migrations for Phase 2 created and applied.
  - Service functions for managing Customers, Suppliers, and Items (Products/Services).
  - Business-wise data isolation applied to all new tables.
  - Opening balance tracking (Dr/Cr) for Customers and Suppliers.
  - UI Tab for Customer Management integrated into main Dashboard.
  - Pytest test suite expanded to cover Phase 2 business logic.

- **Phase 1 Implementation:**
  - Modular project architecture in `accounting_app/`.
  - SQLite database integration using `SQLAlchemy`.
  - Database schema migrations using `Alembic`.
  - Secure password hashing utilities using `bcrypt`.
  - Initial database models: `User`, `Role`, `Business`, `FinancialYear`.
  - Initialization script to seed initial admin user, roles, and two default businesses.
  - Automated test suite for foundation logic.
  - Login screen and Business Selection screen built with `CustomTkinter`.
  - `run.bat` and `install.bat` scripts for easy startup and setup.
