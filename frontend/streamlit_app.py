import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="Smart Irrigation", layout="wide")
st.title("🌱 Smart Irrigation Dashboard")

# --- Latest Sensor Data ---
st.header("🌡️ Temperature & Humidity")
sensor_placeholder = st.empty()

def fetch_latest():
    try:
        r = requests.get(f"{API_BASE}/sensor/latest")
        if r.ok:
            return r.json()
    except:
        return None

sensor = fetch_latest()
if sensor:
    st.metric("Temperature (°C)", sensor["temperature"])
    st.metric("Humidity (%)", sensor["humidity"])
    st.caption(f"Timestamp: {sensor['timestamp']}")
else:
    st.info("No sensor data yet.")

# --- Soil Moisture Chart ---
st.subheader("🌾 Soil Moisture")
r = requests.get(f"{API_BASE}/sensor")
if r.ok:
    df = pd.DataFrame(r.json())
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    if not df.empty:
        st.line_chart(df.set_index("timestamp")["soil_moisture"])
        st.metric("Latest Soil Moisture (%)", f"{df.iloc[-1]['soil_moisture']:.1f}")

# --- Water Level Chart ---
st.subheader("💧 Water Level")
if not df.empty:
    st.line_chart(df.set_index("timestamp")["water_level"])
    st.metric("Latest Water Level (%)", f"{df.iloc[-1]['water_level']:.1f}")

# --- Pump Control ---
st.subheader("🚰 Pump Control")
devices = requests.get(f"{API_BASE}/devices/").json()
DEVICE_ID = devices[0]["id"]

col1, col2 = st.columns(2)
with col1:
    if st.button("Turn Pump ON"):
        res = requests.post(f"{API_BASE}/devices/{DEVICE_ID}/commands", json={"command":"ON"})
        if res.ok:
            st.success("Pump ON")
with col2:
    if st.button("Turn Pump OFF"):
        res = requests.post(f"{API_BASE}/devices/{DEVICE_ID}/commands", json={"command":"OFF"})
        if res.ok:
            st.success("Pump OFF")

# --- Alerts ---
st.subheader("⚠️ Alerts")
alerts = requests.get(f"{API_BASE}/alerts/").json()
st.dataframe(alerts)
