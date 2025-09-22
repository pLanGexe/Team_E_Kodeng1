import os
import requests
import streamlit as st
import pandas as pd
from typing import List, Dict, Any


st.set_page_config(page_title="Device Management", page_icon="📱", layout="wide")
st.title("📱 Device Management System")

# ---------- Real-time Sensor Data Section ----------
st.header("🌡️ Real-time Sensor Data")

def get_latest_sensor_data():
    try:
        response = requests.get(f"{backend_url}/data/latest", timeout=2)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching sensor data: {str(e)}")
        return None

sensor_placeholder = st.empty()

import time
for _ in range(1000):  # Limit loop for safety
    sensor = get_latest_sensor_data()
    if sensor:
        sensor_placeholder.markdown(f"""
        **Timestamp:** {sensor['timestamp']}  
        **Device ID:** {sensor.get('device_id', 'N/A')}  
        **Value:** {sensor['value']}
        """)
    else:
        sensor_placeholder.info("No sensor data available.")
    time.sleep(2)

backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")

# Helper functions for API calls
def get_devices() -> List[Dict[str, Any]]:
    """Fetch all devices from the backend API."""
    try:
        response = requests.get(f"{backend_url}/devices/")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching devices: {str(e)}")
        return []

def create_device(name: str, model: str, location: str = None) -> bool:
    """Create a new device via the backend API."""
    try:
        device_data = {
            "name": name,
            "model": model,
            "location": location if location else None
        }
        response = requests.post(f"{backend_url}/devices/", json=device_data)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Error creating device: {str(e)}")
        return False

def delete_device(device_id: int) -> bool:
    """Delete a device via the backend API."""
    try:
        response = requests.delete(f"{backend_url}/devices/{device_id}")
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Error deleting device: {str(e)}")
        return False

# Main app layout
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📋 Device List")
    
    # Refresh button
    if st.button("🔄 Refresh List", type="secondary"):
        st.rerun()
    
    # Fetch and display devices
    devices = get_devices()
    
    if devices:
        # Convert to DataFrame for better display
        df = pd.DataFrame(devices)
        
        # Display devices in a table with action buttons
        for idx, device in enumerate(devices):
            with st.container():
                device_col1, device_col2, device_col3, device_col4, device_col5 = st.columns([1, 2, 2, 2, 1])
                
                with device_col1:
                    st.write(f"**ID:** {device['id']}")
                
                with device_col2:
                    st.write(f"**Name:** {device['name']}")
                
                with device_col3:
                    st.write(f"**Model:** {device['model']}")
                
                with device_col4:
                    location = device.get('location', 'Not specified')
                    st.write(f"**Location:** {location}")
                
                with device_col5:
                    # Direct delete button
                    if st.button(f"🗑️ Delete", key=f"delete_{device['id']}", type="secondary"):
                        if delete_device(device['id']):
                            st.success(f"Device '{device['name']}' deleted successfully!")
                            st.rerun()
                
                st.divider()
    else:
        st.info("No devices found. Add your first device using the form on the right!")

with col2:
    st.header("➕ Add New Device")
    
    with st.form("add_device_form"):
        st.subheader("Device Information")
        
        device_name = st.text_input(
            "Device Name *", 
            placeholder="e.g., Temperature Sensor #1, Smart Thermostat",
            help="Enter a descriptive name for the device"
        )
        
        device_model = st.text_input(
            "Device Model *", 
            placeholder="e.g., DHT22, ESP32-DevKit, Arduino Uno",
            help="Enter the model number or identifier"
        )
        
        device_location = st.text_input(
            "Location (Optional)", 
            placeholder="e.g., Living Room, Server Room, Greenhouse",
            help="Where is this device located?"
        )
        
        submitted = st.form_submit_button("🚀 Add Device", type="primary", use_container_width=True)
        
        if submitted:
            if not device_name.strip():
                st.error("Device name is required!")
            elif not device_model.strip():
                st.error("Device model is required!")
            else:
                if create_device(device_name.strip(), device_model.strip(), device_location.strip() or None):
                    st.success(f"Device '{device_name}' added successfully!")
                    st.rerun()

# Footer with API status
st.divider()
col1, col2 = st.columns([1, 1])

with col1:
    st.caption(f"Backend URL: {backend_url}")

with col2:
    # Check backend connectivity
    try:
        response = requests.get(f"{backend_url}/hello", timeout=2)
        if response.status_code == 200:
            st.caption("🟢 Backend Connected")
        else:
            st.caption("🟡 Backend Issues")
    except:
        st.caption("🔴 Backend Disconnected")
