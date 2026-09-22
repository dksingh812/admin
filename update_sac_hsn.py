import sqlite3
import re
import os

DB_PATH = os.path.join('Invoicing', 'invoicing.db')

def update_sachsn_no_brackets():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT SACCode, SACName FROM tblSACHSN")
    rows = cursor.fetchall()
    for code, name in rows:
        # Remove anything in brackets
        new_name = re.sub(r'\(.*?\)', '', name).strip()
        cursor.execute("UPDATE tblSACHSN SET SACName = ? WHERE SACCode = ?", (new_name, code))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    update_sachsn_no_brackets()
