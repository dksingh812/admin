# Changelog

## [Unreleased]
### Added
- Modular project architecture in `accounting_app/`.
- SQLite database integration using `SQLAlchemy`.
- Database schema migrations using `Alembic`.
- Secure password hashing utilities using `bcrypt`.
- Initial database models: `User`, `Role`, `Business`, `FinancialYear`.
- Initialization script to seed initial admin user, roles, and two default businesses (PARIGANTAVYA CONSULTANTS, BERIFY & ASSOCIATES).
- Automated test suite for foundation logic.
- Login screen built with `CustomTkinter`.
- Business Selection screen built with `CustomTkinter`.
- `run.bat` and `install.bat` scripts for easy startup and setup.
