from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Body, Query, Depends
from typing import Optional, Annotated
from sqlmodel import Field, Session, SQLModel, create_engine, select
import sqlite3
from datetime import datetime

# ------------------ Models ------------------
class Device(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    model: str
    location: Optional[str] = None

# ------------------ Database ------------------
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    # สร้าง table sensor_data สำหรับเก็บ readings
    conn = sqlite3.connect(sqlite_file_name)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id INTEGER,
            soil_moisture REAL,
            water_level REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            alert_type TEXT,
            message TEXT,
            resolved BOOLEAN DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

# ------------------ FastAPI app ------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

# ------------------ Endpoints ------------------
@app.get("/hello")
def hello():
    return {"message": "Hello, World!"}

# Devices
@app.post("/devices/", response_model=Device)
def create_device(device: Device, session: SessionDep) -> Device:
    session.add(device)
    session.commit()
    session.refresh(device)
    return device

@app.get("/devices/", response_model=list[Device])
def read_devices(session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100):
    return session.exec(select(Device).offset(offset).limit(limit)).all()

# ------------------ Sensor Endpoints ------------------
@app.post("/sensor")
async def receive_sensor(request: Request):
    """
    Wokwi ESP32 จะส่ง JSON เช่น:
    {
      "soil_moisture": 40.5,
      "water_level": 80.2
    }
    """
    data = await request.json()
    soil = data.get("soil_moisture")
    water = data.get("water_level")
    device_id = 1   # สมมติ device เดียว

    conn = sqlite3.connect(sqlite_file_name)
    c = conn.cursor()
    c.execute("INSERT INTO sensor_data (device_id, soil_moisture, water_level) VALUES (?, ?, ?)", (device_id, soil, water))
    conn.commit()
    conn.close()

    # สร้าง alert ถ้าน้ำต่ำ
    if water is not None and water < 20:
        conn = sqlite3.connect(sqlite_file_name)
        c = conn.cursor()
        c.execute("INSERT INTO alerts (alert_type, message) VALUES (?, ?)", ("LOW_WATER", "Water level below 20%"))
        conn.commit()
        conn.close()

    return {"status": "ok"}

@app.get("/devices/{device_id}/readings")
def get_device_readings(device_id: int, start: Optional[str] = None):
    conn = sqlite3.connect(sqlite_file_name)
    c = conn.cursor()

    if start:
        c.execute("SELECT soil_moisture, water_level, timestamp FROM sensor_data WHERE timestamp >= ? AND device_id=? ORDER BY id DESC LIMIT 100", (start, device_id))
    else:
        c.execute("SELECT soil_moisture, water_level, timestamp FROM sensor_data WHERE device_id=? ORDER BY id DESC LIMIT 100", (device_id,))

    rows = c.fetchall()
    conn.close()

    readings = []
    for row in rows:
        readings.append({"device_id": device_id, "sensor_type": "soil_moisture", "value": row[0], "timestamp": row[2]})
        readings.append({"device_id": device_id, "sensor_type": "water_level", "value": row[1], "timestamp": row[2]})
    return readings

# ------------------ Alerts ------------------
@app.get("/alerts/")
def get_alerts():
    conn = sqlite3.connect(sqlite_file_name)
    c = conn.cursor()
    c.execute("SELECT timestamp, alert_type, message, resolved FROM alerts ORDER BY id DESC LIMIT 20")
    rows = c.fetchall()
    conn.close()
    return [{"timestamp": r[0], "alert_type": r[1], "message": r[2], "resolved": bool(r[3])} for r in rows]

# ------------------ Pump Control ------------------
@app.post("/devices/{device_id}/commands")
def pump_command(device_id: int, command: dict = Body(...)):
    cmd = command.get("command")
    if cmd == "ON":
        return {"status": "Pump ON"}
    elif cmd == "OFF":
        return {"status": "Pump OFF"}
    else:
        raise HTTPException(status_code=400, detail="Invalid command")
