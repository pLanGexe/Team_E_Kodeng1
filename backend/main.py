from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import sqlite3
import os
import uvicorn

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "sensor.db")

app = FastAPI()

latest_data = {}

# -----------------------------
# Model สำหรับรับข้อมูลจาก ESP32
# -----------------------------
class SensorData(BaseModel):
    temp: float
    humidity: float
    timestamp: Optional[int] = None  # <- แก้จาก str → int

# -----------------------------
# รับข้อมูลล่าสุดจาก ESP32
# -----------------------------
@app.post("/sensor/latest")
async def post_sensor(data: SensorData):
    global latest_data

    # ถ้า ESP32 ส่ง timestamp มาจะใช้เลย (UTC+7)
    if data.timestamp:
        ts = datetime.fromtimestamp(data.timestamp)
    else:
        # ถ้าไม่ส่ง timestamp มา ใช้เวลาปัจจุบันของไทย
        ts = datetime.utcnow() + timedelta(hours=7)

    latest_data = {
        "temp": data.temp,
        "humidity": data.humidity,
        "timestamp": ts.isoformat()
    }

    # --- LOG ใน terminal ---
    print(f"[{ts}] Temp: {data.temp:.2f} °C | Humidity: {data.humidity:.2f} %")

    # --- INSERT ลง SQLite ---
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO data (humidity, temperature, Time) VALUES (?, ?, ?)",
            (float(data.humidity), float(data.temp), int(ts.timestamp()))
        )
        conn.commit()
        conn.close()
        print(f"Inserted into DB at Time={int(ts.timestamp())}")
    except sqlite3.IntegrityError as e:
        print(f"DB Error: {e}")

    return {"status": "success", "received": latest_data}


# -----------------------------
# ดึงข้อมูลทั้งหมดจากฐานข้อมูล
# -----------------------------
@app.get("/sensor/all")
async def get_all_sensors():
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM data ORDER BY Time DESC")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return {"status": "no data yet", "data": []}

        data_list = []
        for row in rows:
            row_dict = dict(row)
            # แปลง timestamp เป็นเวลาประเทศไทย (UTC+7)
            row_dict["timestamp"] = (
                datetime.fromtimestamp(row_dict["Time"]) + timedelta(hours=7)
            ).isoformat()
            data_list.append(row_dict)

        return {"status": "ok", "data": data_list}

    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
