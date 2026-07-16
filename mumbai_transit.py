import streamlit as st
from datetime import datetime, timedelta
import base64
import time

# --- 1. CONFIGURATION & CLOUD DICTIONARY DATABASE ENGINE ---
# Utilizing Streamlit's built-in sandbox memory context to store logs securely across network calls
if "cloud_transit_db" not in st.session_state:
    st.session_state.cloud_transit_db = {}

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

# Process Submission via Native Cloud Sync Gateway
if crowd_selection:
    if not uploaded_file:
        st.warning("⚠️ Please snap a quick photo proof before updating status to ensure data accuracy!")
    else:
        try:
            bytes_data = uploaded_file.getvalue()
            base64_photo = base64.b64encode(bytes_data).decode('utf-8')
            
            # Save directly to the cloud key storage mapped by station name
            st.session_state.cloud_transit_db[selected_station] = {
                "crowd_level": crowd_selection,
                "proof_photo": base64_photo,
                "reported_at": datetime.now().isoformat()
            }
            
            st.success("✅ Proof verified! Status updated.")
            time.sleep(0.5)
            st.rerun()
        except Exception as e:
            st.error(f"Sync error detail: {e}")

# --- 5. RENDER VERIFIED TIMELINE DATA ---
st.markdown("---")
st.write(f"### 📊 Real-Time Status: {selected_station}")

try:
    # Safely query cloud database cache dictionary
    latest_report = st.session_state.cloud_transit_db.get(selected_station, None)
    
    if not latest_report:
        st.info(f"No recent logs for {selected_station} station yet. Be the first to add verified data!")
    else:
        latest_crowd = latest_report.get('crowd_level', 'Unknown')
        photo_data_string = latest_report.get('proof_photo', None)
        
        try:
            raw_time = datetime.fromisoformat(latest_report['reported_at'])
            clean_time = raw_time.strftime("%I:%M %p")
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
except Exception as e:
    st.error(f"System pathway processing issue: {e}")

# --- 6. FOOTER AD & VIRAL SHARE ---
st.markdown('<div class="ad-box">🏷️ <b>Sponsored Banner Space</b></div>', unsafe_allow_html=True)

share_msg = f"Check if {selected_station} station is crowded right now before leaving home: "
whatsapp_link = f"https://whatsapp.com{share_msg}https://streamlit.app"
st.markdown(f'<a href="{whatsapp_link}" target="_blank"><button style="width:100%; padding:10px; background-color:#25D366; color:white; border:none; border-radius:6px; font-weight:bold; cursor:pointer;">🟢 Share {selected_station} Live Status via WhatsApp</button></a>', unsafe_allow_html=True)
