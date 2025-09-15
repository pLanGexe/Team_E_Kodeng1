# app/backend/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from pydantic import BaseModel, field_serializer

import backend.db as db
from typing import List, Optional

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    db.init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/hello")
def hello():
    return {"message": "Hello, World!"}

@app.get("/count")
def count():
    value = db.increment_and_get("global")
    return {"count": value}