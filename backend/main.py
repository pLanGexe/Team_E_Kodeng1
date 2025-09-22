# app/backend/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query, Depends, HTTPException
from typing import Optional, Annotated
from sqlmodel import Field, Session, SQLModel, create_engine, select

# ---------- Models ----------


# Device Model
class Device(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    model: str
    location: Optional[str] = Field(default=None, index=True)

# SensorData Model สำหรับเก็บข้อมูลจาก Wokwi
class SensorData(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    device_id: Optional[int] = Field(default=None, foreign_key="device.id")
    timestamp: str
    value: float


# ---------- Engine & DB setup ----------

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# For SQLite with FastAPI, allow cross-thread use within a request
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)  # set echo=True to log SQL


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


# ---------- Session dependency ----------

def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

# Example Endpoints
@app.get("/hello")
def hello():
    return {"message": "Hello, World!"}

# Simple counter endpoint
@app.get("/count")
def count():
    value = db.increment_and_get("global")
    return {"count": value}


# Device Endpoints
@app.post("/devices/", response_model=Device)
def create_device(device: Device, session: SessionDep) -> Device:
    session.add(device)
    session.commit()
    session.refresh(device)
    return device

@app.get("/devices/", response_model=list[Device])
def read_devices(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Device]:
    devices = session.exec(select(Device).offset(offset).limit(limit)).all()
    return devices

@app.get("/devices/{device_id}", response_model=Device)
def read_device(device_id: int, session: SessionDep) -> Device:
    device = session.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

@app.delete("/devices/{device_id}")
def delete_device(device_id: int, session: SessionDep):
    device = session.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    session.delete(device)
    session.commit()
    return {"ok": True}

# ---------- Sensor Data Endpoints ----------

# รับข้อมูลจาก Wokwi (POST)
@app.post("/data")
def post_sensor_data(sensor: SensorData, session: SessionDep):
    session.add(sensor)
    session.commit()
    session.refresh(sensor)
    return sensor

# ดึงข้อมูลล่าสุด (GET)
@app.get("/data/latest", response_model=SensorData)
def get_latest_sensor_data(session: SessionDep):
    sensor = session.exec(select(SensorData).order_by(SensorData.timestamp.desc())).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="No sensor data found")
    return sensor