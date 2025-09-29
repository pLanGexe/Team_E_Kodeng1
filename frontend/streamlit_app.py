import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# -------------------------------
# Config
# -------------------------------
API_BASE = "http://localhost:8000"   # URL ของ FastAPI backend
DEVICE_ID = 1                        # สมมติอุปกรณ์ตัวแรก

st.set_page_config(page_title="Smart Irrigation Dashboard", layout="wide")
st.title("🌱 Smart Irrigation System Dashboard")

# -------------------------------
# Helper function
# -------------------------------
def fetch_devices():
    r = requests.get(f"{API_BASE}/devices/")
    if r.ok:
        return r.json()
    return []

def fetch_readings(device_id, sensor_type, hours=12):
    """ดึง readings ล่าสุด n ชั่วโมง"""
    start = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
    params = {"start": start}
    r = requests.get(f"{API_BASE}/devices/{device_id}/readings", params=params)
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
    payload = {"command": command}
    r = requests.post(f"{API_BASE}/devices/{device_id}/commands", json=payload)
    return r.ok

# -------------------------------
# Sidebar – Device selector
# -------------------------------
devices = fetch_devices()
device_names = {d["id"]: d["name"] for d in devices}
if devices:
    DEVICE_ID = st.sidebar.selectbox("Select Device", options=list(device_names.keys()), format_func=lambda x: device_names[x])
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
