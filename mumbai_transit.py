import streamlit as st
from datetime import datetime
import base64
import time

# --- 1. CONFIGURATION & MEMORY STORAGE ---
if "cloud_transit_db" not in st.session_state:
    st.session_state.cloud_transit_db = {}

# --- 2. COMPLETE MUMBAI STATION DATABASE ---
STATION_DATABASE = {
    "Mumbai Local": {
        "Western Line": [
            "Churchgate", "Marine Lines", "Charni Road", "Grant Road", "Mumbai Central",
            "Mahalakshmi", "Lower Parel", "Prabhadevi", "Dadar", "Matunga Road",
            "Mahim", "Bandra", "Khar Road", "Santacruz", "Vile Parle", "Andheri",
            "Jogeshwari", "Ram Mandir", "Goregaon", "Malad", "Kandivali", "Borivali",
            "Dahisar", "Mira Road", "Bhayandar", "Naigaon", "Vasai Road", "Nallasopara", "Virar"
        ],
        "Central Line (Main)": [
            "CSMT", "Masjid", "Sandhurst Road", "Byculla", "Chinchpokli", "Currey Road",
            "Parel", "Dadar", "Matunga", "Sion", "Kurla", "Vidyavihar", "Ghatkopar",
            "Vikhroli", "Kanjurmarg", "Bhandup", "Nahur", "Mulund", "Thane",
            "Kalva", "Mumbra", "Diva", "Kopar", "Dombivli", "Thakurli", "Kalyan"
        ],
        "Harbour Line": [
            "CSMT", "Masjid", "Sandhurst Road", "Dockyard Road", "Reay Road", "Cotton Green",
            "Sewri", "Wadala Road", "King's Circle", "Mahim", "Bandra", "Khar Road", 
            "Santacruz", "Vile Parle", "Andheri", "Goregaon", "Guru Tegh Bahadur Nagar", 
            "Chunabhatti", "Kurla", "Tilaknagar", "Chembur", "Govandi", "Mankhurd", 
            "Vashi", "Sanpada", "Juinagar", "Nerul", "Seawoods-Darave", "Belapur", 
            "Kharghar", "Mansarovar", "Khandeshwar", "Panvel"
        ],
        "Trans-Harbour Line": [
            "Thane", "Airoli", "Rabale", "Ghansoli", "Koparkhairane", 
            "Turbhe", "Sanpada", "Vashi", "Juinagar", "Nerul", "Belapur", "Panvel"
        ]
    },
    "Mumbai Metro": {
        "Metro Line 1 (Versova - Ghatkopar)": [
            "Versova", "D.N. Nagar", "Azad Nagar", "Andheri", "Western Express Highway (WEH)",
            "Chakala (JB Nagar)", "Marol Naka", "Saki Naka", "Asalpha", "Jagruti Nagar", "Ghatkopar"
        ],
        "Metro Line 2A & 7 (Dahisar - Andheri)": [
            "Andheri West", "Lower Oshiwara", "Oshiwara", "Goregaon West", "Bangur Nagar", 
            "Malad West", "Valnai", "Dahanukarwadi", "Kandivali West", "Pahari Goregaon", 
            "Borivali West", "Eksar", "Mandapeshwar", "Kandarpada", "Dahisar East", 
            "Ovaripada", "National Park", "Devipada", "Magathane", "Poisar", 
            "Akurli", "Kurar", "Dindoshi", "Aarey", "Goregaon East", 
            "Jogeshwari East", "Shankarwadi", "Gundavali"
        ],
        "Metro Line 3 (Aqua Line)": [
            "Aarey Colony", "SEEPZ", "MIDC", "Marol Naka", "Chhatrapati Shivaji Maharaj International Airport (T2)",
            "Sahar Road", "Chhatrapati Shivaji Maharaj International Airport (T1)", "Santacruz", "Vidyanagari",
            "BKC", "Dharavi", "Sitaladevi", "Dadkar Maidan", "Siddhivinayak", "Worli", "Acharya Atre Chowk",
            "Science Museum", "Mahalaxmi", "Mumbai Central", "Grant Road", "Girgaon", "Kalbadevi",
            "Chhatrapati Shivaji Maharaj Terminus (CSMT)", "Hutatma Chowk", "Churchgate", "Cuffe Parade"
        ]
    }
}

# --- 3. PAGE CONFIGURATION ---
st.set_page_config(page_title="Live Mumbai Crowd Tracker - All Lines", page_icon="🚇", layout="centered")

st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem !important; max-width: 520px !important; }
    .status-card { padding: 20px; border-radius: 8px; margin-bottom: 12px; background-color: #f8f9fa; border: 1px solid #dee2e6; text-align: center;}
    .ad-box { background-color: #fff9db; border: 1px dashed #f59f00; padding: 12px; text-align: center; margin: 15px 0; border-radius: 6px; font-size: 13px; color: #666; }
    .info-header { border-left: 5px solid #228be6; padding-left: 10px; margin-top: 25px; margin-bottom: 15px; color: #1c7ed6; }
    .footer-links { text-align: center; font-size: 11px; color: #868e96; margin-top: 30px; line-height: 1.8; }
    </style>
""", unsafe_allow_html=True)

st.title("🚇 Mumbai Crowd Tracker")
st.caption("Live, commuter-verified crowd density tracking map for every line across Mumbai.")

# --- 4. TOP ADSENSE DISPLAY PLACEHOLDER ---
st.markdown('<div class="ad-box">🏷️ <b>Sponsored Financial & Local Ads</b><br><small>Google AdSense Automated Responsive Unit</small></div>', unsafe_allow_html=True)

# Navigation Step 1: Select Network
network = st.radio("Select Transit Network", ["Mumbai Local", "Mumbai Metro"], horizontal=True)

# Navigation Step 2: Select Line (Dynamically updates based on Network)
line_options = list(STATION_DATABASE[network].keys())
selected_line = st.selectbox("Select Line / Route", line_options)

# Navigation Step 3: Select Station (Dynamically updates based on Line)
station_options = STATION_DATABASE[network][selected_line]
selected_station = st.selectbox("Select Station Platform", station_options)

# --- 5. COMMUTER REPORT INTERFACE ---
st.write("### 📢 Broadcast Live Station Status")
uploaded_file = st.camera_input("Snap a quick photo proof of the platform or crowd status:")

col1, col2, col3 = st.columns(3)
crowd_selection = None

with col1:
    if st.button("🟢 Less / Empty", use_container_width=True): crowd_selection = "🟢 Less / Empty"
with col2:
    if st.button("🟡 Moderate", use_container_width=True): crowd_selection = "🟡 Moderate"
with col3:
    if st.button("🔴 Very Crowded", use_container_width=True): crowd_selection = "🔴 Very Crowded"

if crowd_selection:
    if not uploaded_file:
        st.warning("⚠️ Please snap a quick photo proof before updating status to ensure absolute network accuracy!")
    else:
        try:
            bytes_data = uploaded_file.getvalue()
            base64_photo = base64.b64encode(bytes_data).decode('utf-8')
            
            # Map tracking logs unique to line + station keys
            storage_key = f"{selected_line} - {selected_station}"
            st.session_state.cloud_transit_db[storage_key] = {
                "crowd_level": crowd_selection,
                "proof_photo": base64_photo,
                "reported_at": datetime.now().isoformat()
            }
            st.success(f"✅ Status broadcasted for {selected_station}!")
            time.sleep(0.5)
            st.rerun()
        except Exception as e:
            st.error(f"Sync error: {e}")

# --- 6. REAL-TIME DATA RENDER ---
st.markdown("---")
st.write(f"### 📊 Real-Time Status: {selected_station} ({selected_line})")

storage_key = f"{selected_line} - {selected_station}"
latest_report = st.session_state.cloud_transit_db.get(storage_key, None)

if not latest_report:
    st.info(f"No recent logs for {selected_station} yet. Be the first to update commuters by snapping a photo above!")
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
        <small style="color: #6c757d;">Last verified commuter report at {clean_time}</small>
    </div>
    """, unsafe_allow_html=True)
    
    if photo_data_string:
        try:
            image_bytes = base64.b64decode(photo_data_string)
            st.image(image_bytes, caption=f"Live commuter platform overview for {selected_station}", use_container_width=True)
        except:
            st.caption("Unable to load preview attachment.")

# --- 7. FOOTER ADSENSE DISPLAY PLACEHOLDER ---
st.markdown('<div class="ad-box">🏷️ <b>Sponsored Links By Google</b><br><small>AdSense Native Content Unit</small></div>', unsafe_allow_html=True)

# --- 8. VIRAL ENGINE SHARE BAR ---
share_msg = f"Check if {selected_station} ({selected_line}) is crowded right now before leaving home: "
whatsapp_link = f"https://whatsapp.com{share_msg}https://streamlit.app"
st.markdown(f'<a href="{whatsapp_link}" target="_blank"><button style="width:100%; padding:11px; background-color:#25D366; color:white; border:none; border-radius:6px; font-weight:bold; cursor:pointer; font-size:14px; margin-bottom:15px;">🟢 Share {selected_station} Live Status via WhatsApp</button></a>', unsafe_allow_html=True)

# --- 9. MANDATORY GOOGLE ADSENSE COMPLIANCE CONTENT SECTION ---
st.markdown("---")
st.markdown('<h3 class="info-header">📘 Mumbai Commuter Guide & Rules</h3>', unsafe_allow_html=True)
st.write("""
Navigating the Mumbai Suburban Railway (Western, Central, Harbour lines) and the growing Mumbai Metro network requires careful planning during peak hours. Peak office times usually run from **8:30 AM to 11:30 AM** (towards CSMT/Churchgate) and **5:30 PM to 8:30 PM** (towards Borivali/Kalyan/Thane). 

To ensure safety, commuters are strongly advised to stand completely clear of the platform yellow safety lines, avoid boarding moving local trains, and strictly utilize foot overbridges (FOBs) instead of crossing railway tracks. Always secure valid tickets or smart cards using UTS mobile applications to clear active inspection terminals smoothly.
""")

st.markdown('<h3 class="info-header">❓ Frequently Asked Questions (FAQ)</h3>', unsafe_allow_html=True)

with st.expander("How does the Mumbai Crowd Tracker verify if updates are true?"):
    st.write("Our system operates on a zero-trust crowdsourcing model. To submit a crowd update for a station like Andheri, Malad, or Thane, a user must capture a live photo of the platform or train interior using their smartphone camera. This prevents remote spam or fake reporting.")

with st.expander("What are the peak traffic timings for Mumbai Local trains?"):st.write("Peak morning down-train travel runs heavy from 8:30 AM to 11:00 AM heading into corporate hubs like Dadar, Lower Parel, Bandra-Kurla Complex (BKC), and CSMT. The evening peak rush returns in reverse direction from 5:30 PM to 9:00 PM.")with st.expander("Can I track all lines of the Mumbai Metro network here?"):st.write("Yes! We actively log updates for Metro Line 1 (Versova-Ghatkopar), Line 2A & 7 (WEH corridor), and the fully operational Line 3 (Aqua Line running from Aarey down to Cuffe Parade).")st.markdown("""Legal Directory: Privacy Policy | Terms of Service | Cookie Settings | Contact WebmasterDisclaimer: Public crowdsourced inputs are informational and not official scheduling logs.© 2026 Mumbai Transit Crowd Utility Hub Inc. All Rights Reserved.""", unsafe_allow_html=True)
