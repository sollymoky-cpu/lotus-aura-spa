import streamlit as st
import pandas as pd
from datetime import datetime
import os
from geopy.geocoders import Nominatim
from streamlit_js_eval import get_geolocation

# Executive Interface Config
st.set_page_config(page_title="Field Force Terminal", layout="centered", initial_sidebar_state="collapsed")

DATA_FILE = "service_records.csv"
ADMIN_PASSWORD = "Sanjay@Admin2026"

if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Timestamp", "Employee Name", "Maps Routing", "Verified Address"])
    df.to_csv(DATA_FILE, index=False)

def get_text_address(lat, lon):
    try:
        geolocator = Nominatim(user_agent="field_force_enterprise_system")
        location = geolocator.reverse(f"{lat}, {lon}", timeout=8)
        return location.address if location else "Coordinates Successfully Logged"
    except:
        return "Coordinates Saved"

query_params = st.query_params
employee_name = query_params.get("name", "").replace("_", " ")

st.markdown("""
    <style>
    .main .block-container { padding-top: 2rem; max-width: 550px; }
    h1 { color: #1E3A8A; font-family: 'Inter', sans-serif; font-weight: 800; text-align: center; font-size: 28px; margin-bottom: 5px; }
    .sub-date { text-align: center; color: #6B7280; font-size: 14px; margin-bottom: 25px; font-weight: 500; }
    
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        padding: 16px 20px !important;
        border-radius: 12px !important;
        border: none !important;
        width: 100% !important;
        box-shadow: 0px 5px 0px #047857, 0px 8px 15px rgba(0, 0, 0, 0.2);
        transition: all 0.1s ease-in-out;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    div.stButton > button:first-child:active {
        transform: translateY(4px) !important;
        box-shadow: 0px 1px 0px #047857, 0px 4px 6px rgba(0, 0, 0, 0.1) !important;
    }
    
    .admin-btn div.stButton > button:first-child {
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%) !important;
        box-shadow: 0px 5px 0px #1D4ED8, 0px 8px 15px rgba(0, 0, 0, 0.15) !important;
        font-size: 16px !important;
        padding: 12px 20px !important;
    }
    
    .user-card { background: #F3F4F6; padding: 20px; border-radius: 14px; border-left: 5px solid #3B82F6; margin-bottom: 20px; }
    .success-card { background: #ECFDF5; padding: 20px; border-radius: 14px; border: 1px solid #A7F3D0; text-align: center; color: #065F46; font-weight: 600; font-size: 16px; box-shadow: 0px 4px 10px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>💼 FIELD FORCE TERMINAL</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='sub-date'>Operational Date: {datetime.now().strftime('%d — %B — %Y')}</div>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📲 Mobile Terminal", "📊 Executive Analytics"])

# ================= EMPLOYEE TERMINAL =================
with tab1:
    if not employee_name:
        st.error("❌ System Access Denied: Invalid Security Token.")
    else:
        st.markdown(f"""
        <div class='user-card'>
            <span style='color:#4B5563; font-size:12px; font-weight:600; text-transform:uppercase;'>Authorized Executive</span>
            <div style='color:#111827; font-size:22px; font-weight:700;'>{employee_name}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if "verified_user" not in st.session_state:
            st.session_state.verified_user = False

        if not st.session_state.verified_user:
            # Active fetch trigger
            loc = get_geolocation()
            
            trigger_checkin = st.button("PROCEED ENTERPRISE CHECK-IN ✔️")

            if loc and 'coords' in loc:
                try:
                    lat = loc['coords']['latitude']
                    lon = loc['coords']['longitude']
                    
                    readable_address = get_text_address(lat, lon)
                    maps_link = f"https://www.google.com/maps?q={lat},{lon}"
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Logic to immediately verify and pipe data to registry
                    new_data = pd.DataFrame([[timestamp, employee_name, maps_link, readable_address]], 
                                            columns=["Timestamp", "Employee Name", "Maps Routing", "Verified Address"])
                    new_data.to_csv(DATA_FILE, mode='a', header=False, index=False)
                    
                    st.session_state.verified_user = True
                    st.rerun()
                except Exception as e:
                    pass
            
            if trigger_checkin and not loc:
                st.info("🔄 Syncing device handshake... Please ensure your device location/GPS is turned ON and browser permission is click-allowed to finalize submission.")

        if st.session_state.verified_user:
            st.markdown(f"""
            <div class='success-card'>
                🎉 Check-In Status: Verified!<br>
                <span style='font-size:13px; font-weight:400; color:#047857;'>Your tactical duty logs have been submitted to enterprise registry.</span>
            </div>
            """, unsafe_allow_html=True)
            st.balloons()

# ================= MANAGEMENT CONTROL DASHBOARD =================
with tab2:
    st.subheader("🔐 Management Authentication")
    
    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False
        
    admin_pass = st.text_input("Enter Control Password", type="password")
    
    st.markdown("<div class='admin-btn'>", unsafe_allow_html=True)
    login_click = st.button("AUTHENTICATE CONTROL PANEL 🔑")
    st.markdown("</div>", unsafe_allow_html=True)
    
    if login_click:
        if admin_pass == ADMIN_PASSWORD:
            st.session_state.admin_logged_in = True
        else:
            st.session_state.admin_logged_in = False
            st.error("❌ Authentication Failed: Invalid Control Credentials.")
            
    if st.session_state.admin_logged_in:
        st.success("Authorized Session Verified!")
        
        df_records = pd.read_csv(DATA_FILE)
        
        st.markdown("### 📊 Operational Live Sync Data")
        st.dataframe(
            df_records.iloc[::-1], 
            use_container_width=True,
            column_config={
                "Maps Routing": st.column_config.LinkColumn("Maps Routing", display_text="Open Live Map 🗺️")
            }
        )
        
        csv = df_records.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Enterprise CSV Log",
            data=csv,
            file_name=f"Enterprise_Report_{datetime.now().strftime('%Y-%m-%d')}.csv",
            mime='text/csv',
        )
