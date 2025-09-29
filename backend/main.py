from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime

# ----------------- DATABASE -----------------
DATABASE_URL = "http://localhost:8000"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ----------------- MODELS -----------------
class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    soil_moisture = Column(Float, nullable=True)
    water_level = Column(Float, nullable=True)
    timestamp = Column(String, default=datetime.utcnow().isoformat)

Base.metadata.create_all(bind=engine)

# ----------------- SCHEMA -----------------
class SensorDataCreate(BaseModel):
    temperature: float | None = None
    humidity: float | None = None
    soil_moisture: float | None = None
    water_level: float | None = None
    timestamp: str | None = None

# ----------------- APP -----------------
app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------- ROUTES -----------------
@app.post("/sensor")
def create_sensor_data(data: SensorDataCreate, db: Session = Depends(get_db)):
    sensor_entry = SensorData(
        temperature=data.temperature,
        humidity=data.humidity,
        soil_moisture=data.soil_moisture,
        water_level=data.water_level,
        timestamp=data.timestamp or datetime.utcnow().isoformat(),
    )
    db.add(sensor_entry)
    db.commit()
    db.refresh(sensor_entry)
    return {"status": "success", "id": sensor_entry.id}

@app.get("/sensor")
def get_all_data(db: Session = Depends(get_db)):
    return db.query(SensorData).all()

@app.get("/sensor/latest")
def get_latest_data(db: Session = Depends(get_db)):
    return db.query(SensorData).order_by(SensorData.id.desc()).first()
