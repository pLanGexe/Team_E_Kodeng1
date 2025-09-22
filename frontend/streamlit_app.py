# frontend/streamlit_app.py
import streamlit as st
import requests
import time

backend_url = "http://localhost:8000"  # เปลี่ยนถ้า backend ใช้ network/container IP

st.set_page_config(page_title="Smart System", layout="wide")
st.title("🌱 Smart System Board")

st.header("🌡️ Realtime Sensor Data")
sensor_placeholder = st.empty()

for _ in range(1000):
    try:
        sensor = requests.get(f"{backend_url}/sensor/latest", timeout=2).json()
        if sensor:
            sensor_placeholder.markdown(f"""
            **Timestamp:** {sensor['timestamp']}  
            **Temperature (°C):** {sensor['temp']}  
            **Humidity (%):** {sensor['humidity']}
            """)
        else:
            sensor_placeholder.info("No sensor data available.")
    except requests.exceptions.RequestException as e:
        sensor_placeholder.error(f"Error fetching sensor data: {str(e)}")
    time.sleep(2)
