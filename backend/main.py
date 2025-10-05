from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import sqlite3
import os
import uvicorn

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "sensor.db")

app = FastAPI()

# ✅ เพิ่ม CORS Middleware เพื่อให้ Streamlit เรียก API ได้จากภายนอก
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # อนุญาตทุกโดเมน (หรือระบุ Streamlit URL ก็ได้)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

latest_data = {}

# -----------------------------
# Model สำหรับรับข้อมูลจาก ESP32
# -----------------------------
class SensorData(BaseModel):
    temp: float
    humidity: float
    timestamp: Optional[int] = None  # timestamp จาก ESP32 (หน่วย: วินาที)


# -----------------------------
# รับข้อมูลล่าสุดจาก ESP32
# -----------------------------
@app.post("/sensor/latest")
async def post_sensor(data: SensorData):
    global latest_data

    if data.timestamp:
        # ✅ ใช้ timestamp ที่ส่งมาจาก ESP32 (ไม่เปลี่ยน)
        ts_raw = datetime.fromtimestamp(data.timestamp)
        # ✅ แต่บันทึกใน DB เป็นเวลาไทย (+7 ชั่วโมง)
        ts_th = ts_raw + timedelta(hours=7)
    else:
        # ถ้า ESP32 ไม่ส่งมา ใช้เวลาปัจจุบันของไทย
        ts_raw = datetime.utcnow()
        ts_th = ts_raw + timedelta(hours=7)

    latest_data = {
        "temp": data.temp,
        "humidity": data.humidity,
        "timestamp": ts_raw.isoformat()  # ใช้เวลาที่ส่งมาจาก ESP32
    }

    print(f"[{ts_raw}] Temp: {data.temp:.2f} °C | Humidity: {data.humidity:.2f} %")

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO data (humidity, temperature, Time) VALUES (?, ?, ?)",
            (float(data.humidity), float(data.temp), int(ts_th.timestamp()))
        )
        conn.commit()
        conn.close()
        print(f"Inserted into DB (Thai Time={ts_th})")
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
            # DB เก็บเป็นเวลาไทยแล้ว
            row_dict["timestamp"] = datetime.fromtimestamp(row_dict["Time"]).isoformat()
            data_list.append(row_dict)

        return {"status": "ok", "data": data_list}

    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
