from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import datetime
import uvicorn

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

    # --- LOG ใน terminal ---
    print(f"[{data.timestamp}] Temp: {data.temp} °C | Humidity: {data.humidity} %")

    return {"status": "success", "received": latest_data}

@app.get("/sensor/latest")
async def get_sensor():
    if not latest_data:
        return {"status": "no data yet"}
    return {"status": "ok", "latest": latest_data}


if __name__ == "__main__":
    #กด run ได้เลย
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
