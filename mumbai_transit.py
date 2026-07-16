import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import time

# --- 1. LOCAL BULLETPROOF DATABASE SETUP ---
DB_FILE = "transit_data.db"

def init_local_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transit_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transit_type TEXT,
            station_name TEXT,
            crowd_level TEXT,
            reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# Initialize the local database automatically on start
init_local_db()

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
st.caption("Simple, minimal real-time station density tracker.")

# --- 4. TOP AD PLACEHOLDER ---
st.markdown('<div class="ad-box">🏷️ <b>Sponsored Banner Space</b></div>', unsafe_allow_html=True)

# --- 5. CATEGORY SWITCHER ---
category = st.radio("Select Network", ["Mumbai Local", "Mumbai Metro"], horizontal=True)

if category == "Mumbai Local":
    selected_station = st.selectbox("Select Station", sorted(MUMBAI_LOCALS))
else:
    selected_station = st.selectbox("Select Station", sorted(MUMBAI_METRO))

# --- 6. SIMPLE REPORT BUTTONS ---
st.write("### 📢 Tap Current Crowd Status:")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🟢 Less / Empty", use_container_width=True):
        crowd_selection = "🟢 Less / Empty"
with col2:
    if st.button("🟡 Moderate", use_container_width=True):
        crowd_selection = "🟡 Moderate"
with col3:
    if st.button("🔴 Very Crowded", use_container_width=True):
        crowd_selection = "🔴 Very Crowded"

# Database sync trigger on click via clean local engine
if 'crowd_selection' in locals():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO transit_reports (transit_type, station_name, crowd_level, reported_at)
            VALUES (?, ?, ?, datetime('now'))
        """, (category, selected_station, crowd_selection))
        conn.commit()
        conn.close()
        
        st.success(f"Updated status for {selected_station}!")
        time.sleep(0.5)
        st.rerun()
    except Exception as e:
        st.error(f"Sync Issue: {e}")

# --- 7. REAL-TIME SUMMARY LOGS ---
st.markdown("---")
st.write(f"### 📊 Real-Time Status: {selected_station}")

try:
    conn = sqlite3.connect(DB_FILE)
    # Query the absolute latest entry for the currently highlighted platform
    query = "SELECT crowd_level, reported_at FROM transit_reports WHERE station_name = ? ORDER BY reported_at DESC LIMIT 1"
    df = pd.read_sql_query(query, conn, params=(selected_station,))
    conn.close()
    
    if df.empty:
        st.info(f"No recent logs for {selected_station} station yet. Try clicking a status button above!")
    else:
        latest_crowd = df.iloc[0]['crowd_level']
        raw_time_str = df.iloc[0]['reported_at']
        
        try:
            # Parse SQLite default timestamp format and shift cleanly into Indian Standard Time
            raw_time = datetime.strptime(raw_time_str, "%Y-%m-%d %H:%M:%S")
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
except Exception as e:
    st.error("Failed to read historical timeline data.")

# --- 8. FOOTER AD & VIRAL SHARE ---
st.markdown('<div class="ad-box">🏷️ <b>Sponsored Banner Space</b></div>', unsafe_allow_html=True)

share_msg = f"Check if {selected_station} station is crowded right now before leaving home: "
whatsapp_link = f"https://whatsapp.com{share_msg}https://streamlit.app"
st.markdown(f'<a href="{whatsapp_link}" target="_blank"><button style="width:100%; padding:10px; background-color:#25D366; color:white; border:none; border-radius:6px; font-weight:bold; cursor:pointer;">🟢 Share {selected_station} Live Status via WhatsApp</button></a>', unsafe_allow_html=True)
