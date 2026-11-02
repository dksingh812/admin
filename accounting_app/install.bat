@echo off
echo Installing requirements...
pip install -r requirements.txt
echo Initializing database...
alembic upgrade head
python src/utils/init_db_data.py
echo Installation complete!
pause
