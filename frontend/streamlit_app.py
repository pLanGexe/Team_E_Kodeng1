import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

# -------------------------------
# Config
# -------------------------------
API_BASE = os.getenv("BACKEND_URL", "http://localhost:8000")  # URL backend

st.set_page_config(page_title="Smart System", layout="wide")
st.title("🌱 Smart System Board")

# -------------------------------
# Real-time Sensor Data (Wokwi)
# -------------------------------
st.header("🌡️ Realtime Sensor Data (Temperature & Humidity)")

# สร้าง placeholder และ DataFrame สำหรับกราฟย้อนหลัง
temp_placeholder = st.empty()
hum_placeholder = st.empty()
chart_placeholder = st.empty()
df_history = pd.DataFrame(columns=["timestamp", "temp", "humidity"])

# ดึงข้อมูลล่าสุด
def get_latest_sensor():
    try:
        r = requests.get(f"{API_BASE}/sensor/latest", timeout=2)
        r.raise_for_status()
        return r.json()
    except:
        return None

# Loop Realtime (polling)
for _ in range(1000):
    sensor = get_latest_sensor()
    if sensor and sensor["temp"] is not None:
        timestamp = pd.to_datetime(sensor["timestamp"])
        df_history = pd.concat([df_history, pd.DataFrame([{
            "timestamp": timestamp,
            "temp": sensor["temp"],
            "humidity": sensor["humidity"]
        }])]).tail(50)  # เก็บล่าสุด 50 records

        temp_placeholder.metric("Temperature (°C)", f"{sensor['temp']:.1f}")
        hum_placeholder.metric("Humidity (%)", f"{sensor['humidity']:.1f}")

        chart_placeholder.line_chart(df_history.set_index("timestamp")[["temp", "humidity"]])
    else:
        st.warning("No sensor data available.")
    time.sleep(2)

# -------------------------------
# Helper functions for existing devices/soil/water/alerts
# -------------------------------
def fetch_devices():
    r = requests.get(f"{API_BASE}/devices/")
    if r.ok:
        return r.json()
    return []

def fetch_readings(device_id, sensor_type, hours=12):
    start = (datetime.utcnow() - pd.Timedelta(hours=hours)).isoformat()
    r = requests.get(f"{API_BASE}/devices/{device_id}/readings", params={"start": start})
    if r.ok:
        df = pd.DataFrame(r.json())
        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df[df["sensor_type"] == sensor_type]
        return df
    return pd.DataFrame()

def fetch_alerts():
    r = requests.get(f"{API_BASE}/alerts/")
    if r.ok:
        return pd.DataFrame(r.json())
    return pd.DataFrame()

def send_pump_command(device_id, command):
    r = requests.post(f"{API_BASE}/devices/{device_id}/commands", json={"command": command})
    return r.ok

# -------------------------------
# Sidebar – Device selector
# -------------------------------
devices = fetch_devices()
device_names = {d["id"]: d["name"] for d in devices}
if devices:
    DEVICE_ID = st.sidebar.selectbox(
        "Select Device",
        options=list(device_names.keys()),
        format_func=lambda x: device_names[x]
    )
else:
    st.sidebar.warning("No devices found")

# -------------------------------
# Soil Moisture Section
# -------------------------------
st.subheader("🌾 Soil Moisture")
soil_df = fetch_readings(DEVICE_ID, "soil_moisture")
if not soil_df.empty:
    st.line_chart(soil_df.set_index("timestamp")["value"])
    st.metric("Latest Soil Moisture (%)", f"{soil_df.iloc[-1]['value']:.1f}%")
else:
    st.info("No soil moisture data yet")

# -------------------------------
# Water Level Section
# -------------------------------
st.subheader("💧 Water Level")
water_df = fetch_readings(DEVICE_ID, "water_level")
if not water_df.empty:
    st.line_chart(water_df.set_index("timestamp")["value"])
    st.metric("Latest Water Level (%)", f"{water_df.iloc[-1]['value']:.1f}%")
else:
    st.info("No water level data yet")

# -------------------------------
# Alerts Section
# -------------------------------
st.subheader("⚠️ Alerts")
alerts_df = fetch_alerts()
if not alerts_df.empty:
    st.dataframe(alerts_df[["timestamp", "alert_type", "message", "resolved"]])
else:
    st.success("No alerts")

# -------------------------------
# Pump Control Section
# -------------------------------
st.subheader("🚰 Pump Control")
col1, col2 = st.columns(2)
with col1:
    if st.button("Turn Pump ON"):
        if send_pump_command(DEVICE_ID, "ON"):
            st.success("Pump turned ON")
        else:
            st.error("Failed to send command")
with col2:
    if st.button("Turn Pump OFF"):
        if send_pump_command(DEVICE_ID, "OFF"):
            st.success("Pump turned OFF")
        else:
            st.error("Failed to send command")
