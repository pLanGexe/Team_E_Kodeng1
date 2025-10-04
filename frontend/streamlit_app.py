import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz
import time

API_URL = "https://psychic-couscous-7644xg6rvpp2p4wg-8001.app.github.dev/sensor/all"

st.set_page_config(page_title="Sensor Monitor", layout="wide")
st.title("🌡️ Sensor Dashboard")
st.write("ดึงข้อมูลจาก FastAPI และแสดงผลแบบเรียลไทม์")

# Containers
time_container = st.empty()
table_container = st.empty()
metrics_container = st.empty()

REFRESH_INTERVAL = 2  # วินาที

# ตั้ง timezone เป็นเวลาประเทศไทย
bangkok_tz = pytz.timezone("Asia/Bangkok")

while True:
    # --- เวลา ณ ขณะนี้ (กรุงเทพ) ---
    now = datetime.now(bangkok_tz).strftime("%Y-%m-%d %H:%M:%S")
    time_container.markdown(f"🕒 <div style='text-align:right; font-size:20px;'>เวลาปัจจุบัน (กรุงเทพ): {now}</div>", unsafe_allow_html=True)

    try:
        response = requests.get(API_URL, timeout=5)
        data = response.json()
    except Exception as e:
        st.error(f"API Error: {e}")
        data = None

    if data and data.get("status") == "ok":
        sensor_list = data["data"]

        if len(sensor_list) > 0:
            # แปลงข้อมูลเป็น DataFrame
            df = pd.DataFrame(sensor_list)
            df["Time"] = pd.to_datetime(df["Time"], unit="s")

            # --- แสดงตารางทั้งหมด ---
            table_container.dataframe(df)

            # --- คำนวณค่าเฉลี่ย ---
            avg_temp = df["temperature"].mean()
            avg_hum = df["humidity"].mean()

            # --- ค่าล่าสุด ---
            latest = sensor_list[0]

            # --- แสดงผลแบบแถวเดียวกัน ---
            with metrics_container.container():
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("🌡️ Temperature (°C)", f"{latest['temperature']:.2f} °C")
                col2.metric("💧 Humidity (%)", f"{latest['humidity']:.2f} %")
                col3.metric("🌡️ Avg Temp (°C)", f"{avg_temp:.2f} °C")
                col4.metric("💧 Avg Humidity (%)", f"{avg_hum:.2f} %")

    else:
        st.warning("ยังไม่มีข้อมูลใน Database")

    time.sleep(REFRESH_INTERVAL)
