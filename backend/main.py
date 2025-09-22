# backend/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Request, Query
from typing import Optional, Annotated
from sqlmodel import Field, Session, SQLModel, create_engine, select
import sqlite3

# ------------------ Models ------------------

class Device(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    model: str
    location: Optional[str] = None

class SensorData(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    device_id: Optional[int] = Field(default=None, foreign_key="device.id")
    timestamp: str
    value: float

# ------------------ Database ------------------

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

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

@app.post("/devices/", response_model=Device)
def create_device(device: Device, session: SessionDep) -> Device:
    session.add(device)
    session.commit()
    session.refresh(device)
    return device

@app.get("/devices/", response_model=list[Device])
def read_devices(session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100):
    return session.exec(select(Device).offset(offset).limit(limit)).all()

# Sensor data endpoints

@app.post("/sensor")
async def receive_sensor(request: Request):
    data = await request.json()
    temp = data.get("temp")
    humidity = data.get("humidity")
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute(
        "CREATE TABLE IF NOT EXISTS sensor_data (id INTEGER PRIMARY KEY AUTOINCREMENT, temp REAL, humidity REAL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)"
    )
    c.execute("INSERT INTO sensor_data (temp, humidity) VALUES (?, ?)", (temp, humidity))
    conn.commit()
    conn.close()
    return {"status": "ok"}

@app.get("/sensor/latest")
def get_latest_sensor():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute(
        "SELECT temp, humidity, timestamp FROM sensor_data ORDER BY id DESC LIMIT 1"
    )
    row = c.fetchone()
    conn.close()
    if row:
        return {"temp": row[0], "humidity": row[1], "timestamp": row[2]}
    else:
        return {"temp": None, "humidity": None, "timestamp": None}
