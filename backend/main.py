from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import datetime
import uvicorn
import sqlite3
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "sensor.db")

app = FastAPI()

latest_data = {}

class SensorData(BaseModel):
    temp: float
    humidity: float
    timestamp: Optional[str] = None

@app.post("/sensor/latest")
async def post_sensor(data: SensorData):
    global latest_data
    data.timestamp = datetime.datetime.now().isoformat()
    latest_data = data.dict()
    now = datetime.datetime.now()



    # --- LOG ใน terminal ---
    print(f"[{data.timestamp}] Temp: {data.temp} °C | Humidity: {data.humidity} %")
    # --- INSERT ลง SQLite ---
    try:
        conn = sqlite3.connect(DB_FILE)   # ใช้ DB_FILE ตาม directory ของไฟล์
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO data (humidity, temperature, Time) VALUES (?, ?, ?)",
            (float(data.humidity), float(data.temp), int(now.timestamp()))
        )
        conn.commit()
        conn.close()
        print(f"Inserted into DB at Time={int(now.timestamp())}")
    except sqlite3.IntegrityError as e:
        print(f"DB Error: {e}")

    return {"status": "success", "received": latest_data}


@app.get("/sensor/latest")
#async def get_sensor():
#    if not latest_data:
#        return {"status": "no data yet"}
#    return {"status": "ok", "latest": latest_data}

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
            row_dict["timestamp"] = datetime.datetime.fromtimestamp(row_dict["Time"]).isoformat()
            data_list.append(row_dict)

        return {"status": "ok", "data": data_list}

    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    #กด run ได้เลย
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
