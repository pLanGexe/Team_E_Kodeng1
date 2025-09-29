from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, Integer, Float, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
from typing import List

# ----------------- DATABASE -----------------
DATABASE_URL = "sqlite:///./sensor.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# ----------------- MODELS -----------------
class SensorData(Base):
    __tablename__ = "sensor_data"
    id = Column(Integer, primary_key=True, index=True)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    soil_moisture = Column(Float, nullable=True)
    water_level = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# ----------------- SCHEMA -----------------
class SensorDataCreate(BaseModel):
    temperature: float | None = None
    humidity: float | None = None
    soil_moisture: float | None = None
    water_level: float | None = None
    timestamp: datetime | None = None

# ----------------- APP -----------------
app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------- SENSOR ENDPOINT -----------------
@app.post("/sensor")
def create_sensor_data(data: SensorDataCreate, db: Session = Depends(get_db)):
    entry = SensorData(
        temperature=data.temperature,
        humidity=data.humidity,
        soil_moisture=data.soil_moisture,
        water_level=data.water_level,
        timestamp=data.timestamp or datetime.utcnow()
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return {"status": "success", "id": entry.id}

@app.get("/sensor", response_model=List[SensorDataCreate])
def get_all_data(db: Session = Depends(get_db)):
    return db.query(SensorData).all()

@app.get("/sensor/latest")
def get_latest_data(db: Session = Depends(get_db)):
    return db.query(SensorData).order_by(SensorData.id.desc()).first()

# ----------------- DEVICES / PUMP CONTROL -----------------
devices = [{"id": 1, "name": "Irrigation Pump 1"}]
pump_state = {"1": "OFF"}  # เก็บสถานะ pump

@app.get("/devices/")
def get_devices():
    return devices

@app.post("/devices/{device_id}/commands")
def control_pump(device_id: int, payload: dict):
    cmd = payload.get("command")
    if str(device_id) in pump_state:
        pump_state[str(device_id)] = cmd
    return {"status": "success", "device_id": device_id, "command": cmd}

@app.get("/alerts/")
def get_alerts():
    # Mock alerts
    return [
        {"timestamp": datetime.utcnow().isoformat(), "alert_type": "Low Water", "message": "Water level < 30%", "resolved": False}
    ]
