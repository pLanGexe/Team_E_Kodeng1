import sqlite3

# กำหนดชื่อไฟล์ฐานข้อมูล
DB_FILE = "sensor.db"

# คำสั่ง SQL สำหรับสร้างตาราง
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS data (
    humidity REAL,
    temperature REAL,
    Time INTEGER PRIMARY KEY
);
"""

def create_table():
    conn = sqlite3.connect(DB_FILE)   # เชื่อมต่อ (ถ้าไม่มีไฟล์ จะสร้างใหม่)
    cursor = conn.cursor()
    cursor.execute(CREATE_TABLE_SQL)  # สร้างตาราง
    conn.commit()
    conn.close()
    print("Table 'data' created (if not exists).")

if __name__ == "__main__":
    create_table()