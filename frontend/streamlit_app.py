import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

API_URL = "https://psychic-couscous-7644xg6rvpp2p4wg-8001.app.github.dev/sensor/all"

st.set_page_config(page_title="Sensor Monitor", layout="wide")
st.title("🌡️ Sensor Dashboard")
st.write("ดึงข้อมูลจาก FastAPI และแสดงผลแบบเรียลไทม์")

# Containers สำหรับอัปเดตตารางและค่าล่าสุด
table_container = st.empty()
temp_container = st.empty()
hum_container = st.empty()

REFRESH_INTERVAL = 2  # วินาที

while True:
    try:
        response = requests.get(API_URL, timeout=5)
        data = response.json()
    except Exception as e:
        st.error(f"API Error: {e}")
        data = None

    if data and data.get("status") == "ok":
        sensor_list = data["data"]

        if len(sensor_list) > 0:
            # แปลงเป็น DataFrame
            df = pd.DataFrame(sensor_list)
            df["Time"] = pd.to_datetime(df["Time"], unit="s")

            # --- แสดงตารางทั้งหมด ---
            table_container.dataframe(df)

            # --- แสดงค่าล่าสุด (row แรก) ---
            latest = sensor_list[0]
            temp_container.metric("Temperature (°C)", f"{latest['temperature']} °C")
            hum_container.metric("Humidity (%)", f"{latest['humidity']} %")
    else:
        st.warning("ยังไม่มีข้อมูลใน Database")

    time.sleep(REFRESH_INTERVAL)
