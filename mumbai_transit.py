import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import base64
import time

# --- 1. CONFIGURATION & EXACT ENDPOINT ROUTING ---
# FIXED: Separated endpoints clearly to prevent Python string squashing bugs
BASE_URL = "https://supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxvYmxrcXhzeGxjbW1hbXdqaWJwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODQyMTE4NDQsImV4cCI6MjA5OTc4Nzg0NH0.Vi7nYkCBUCnZvpNviQ8Ps__RHp5_BlIMx6lCWVmx-QE"

HEADERS = {
    "apikey": KEY,
    "Authorization": f"Bearer {KEY}",
    "Content-Type": "application/json"
}

# --- 2. STATION DIRECTORY ---
MUMBAI_LOCALS = ["Malad", "Churchgate", "Dadar", "Bandra", "Andheri", "Borivali", "CSMT", "Byculla", "Kurla", "Ghatkopar", "Thane", "Kalyan", "Vashi", "Panvel"]
MUMBAI_METRO = ["Versova", "D.N. Nagar", "Azad Nagar", "Andheri (Metro)", "WEH", "Chakala", "Marol Naka", "Saki Naka", "Asalpha", "Ghatkopar (Metro)", "Gundavali", "Dahisar East", "BKC"]

# --- 3. PAGE CONFIGURATION ---
st.set_page_config(page_title="Live Crowd Tracker", page_icon="🚇", layout="centered")

st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem !important; max-width: 480px !important; }
    .status-card { padding: 20px; border-radius: 8px; margin-bottom: 12px; background-color: #f8f9fa; border: 1px solid #dee2e6; text-align: center;}
    .ad-box { background-color: #fff9db; border: 1px dashed #f59f00; padding: 10px; text-align: center; margin: 15px 0; border-radius: 6px; font-size: 13px; color: #666; }
    </style>
""", unsafe_allow_html=True)

st.title("🚇 Mumbai Crowd Tracker")
st.caption("Verified real-time station density data logs.")

st.markdown('<div class="ad-box">🏷️ <b>Sponsored Banner Space</b></div>', unsafe_allow_html=True)

category = st.radio("Select Network", ["Mumbai Local", "Mumbai Metro"], horizontal=True)
selected_station = st.selectbox("Select Station", sorted(MUMBAI_LOCALS) if category == "Mumbai Local" else sorted(MUMBAI_METRO))

# --- 4. PROOF VERIFICATION INTERFACE ---
st.write("### 📢 Broadcast Status with Proof")
uploaded_file = st.camera_input("Take a quick photo of the station platform/crowd:")

col1, col2, col3 = st.columns(3)
crowd_selection = None

with col1:
    if st.button("🟢 Less / Empty", use_container_width=True): crowd_selection = "🟢 Less / Empty"
with col2:
    if st.button("🟡 Moderate", use_container_width=True): crowd_selection = "🟡 Moderate"
with col3:
    if st.button("🔴 Very Crowded", use_container_width=True): crowd_selection = "🔴 Very Crowded"

# Push using backend function endpoint
if crowd_selection:
    if not uploaded_file:
        st.warning("⚠️ Please snap a quick photo proof before updating status to ensure data accuracy!")
    else:
        try:
            bytes_data = uploaded_file.getvalue()
            base64_photo = base64.b64encode(bytes_data).decode('utf-8')
            
            payload = {
                "p_transit_type": category,
                "p_station_name": selected_station,
                "p_crowd_level": crowd_selection,
                "p_proof_photo": base64_photo
            }
            
            # FIXED: Forced clear explicit forward slash separation
            post_url = f"{BASE_URL}/accept_commuter_report"
            response = requests.post(post_url, headers=HEADERS, json=payload)
            
            if response.status_code == 200 or response.status_code == 201:
                st.success("✅ Proof verified! Status updated.")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error(f"Sync Issue. Server Code: {response.status_code}")
        except Exception as e:
            st.error(f"Sync error detail: {e}")

# --- 5. RENDER VERIFIED TIMELINE DATA ---
st.markdown("---")
st.write(f"### 📊 Real-Time Status: {selected_station}")

try:
    fetch_payload = {"p_station_name": selected_station}
    # FIXED: Forced clear explicit forward slash separation
    get_url = f"{BASE_URL}/fetch_latest_report"
    response = requests.post(get_url, headers=HEADERS, json=fetch_payload)
    
    if response.status_code == 200:
        station_logs = response.json()
        
        if not station_logs or len(station_logs) == 0:
            st.info(f"No recent logs for {selected_station} station yet. Be the first to add verified data!")
        else:
            latest_report = station_logs[0]  # Array dictionary safe indexing
            latest_crowd = latest_report.get('crowd_level', 'Unknown')
            photo_data_string = latest_report.get('proof_photo', None)
            
            try:
                raw_time = datetime.fromisoformat(latest_report['reported_at'].replace('Z', '+00:00'))
                ist_time = raw_time + timedelta(hours=5, minutes=30)
                clean_time = ist_time.strftime("%I:%M %p")
            except:
                clean_time = "Just now"

            st.markdown(f"""
            <div class="status-card">
                <span style="font-size: 24px; font-weight: bold;">{latest_crowd}</span><br>
                <small style="color: #6c757d;">Last commuter report at {clean_time}</small>
            </div>
            """, unsafe_allow_html=True)
            
            if photo_data_string:
                try:
                    image_bytes = base64.b64decode(photo_data_string)
                    st.image(image_bytes, caption=f"Live commuter proof image for {selected_station}", use_container_width=True)
                except:
                    st.caption("Unable to load preview attachment.")
    else:
        st.error(f"Failed to fetch timeline status logs. Server response: {response.status_code}")
except Exception as e:
    st.error(f"System pathway processing issue: {e}")

# --- 6. FOOTER AD & VIRAL SHARE ---
st.markdown('<div class="ad-box">🏷️ <b>Sponsored Banner Space</b></div>', unsafe_allow_html=True)

share_msg = f"Check if {selected_station} station is crowded right now before leaving home: "
whatsapp_link = f"https://whatsapp.com{share_msg}https://streamlit.app"
st.markdown(f'<a href="{whatsapp_link}" target="_blank"><button style="width:100%; padding:10px; background-color:#25D366; color:white; border:none; border-radius:6px; font-weight:bold; cursor:pointer;">🟢 Share {selected_station} Live Status via WhatsApp</button></a>', unsafe_allow_html=True)
