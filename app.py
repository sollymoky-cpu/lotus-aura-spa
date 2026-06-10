import streamlit as st
import pandas as pd
from datetime import datetime
import os
from geopy.geocoders import Nominatim
from streamlit_js_eval import get_geolocation

# Page Configuration - Standard Branding
st.set_page_config(page_title="Field Service Portal", layout="centered")

DATA_FILE = "service_records.csv"
PASSWORD = "Sanjay@Admin2026"  # Aapka naya strong aur easy password

# Initialize CSV Database
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Timestamp", "Employee Name", "Text Address", "Google Maps Link"])
    df.to_csv(DATA_FILE, index=False)

# Reverse Geocoding Function
def get_text_address(lat, lon):
    try:
        geolocator = Nominatim(user_agent="field_service_enterprise_portal")
        location = geolocator.reverse(f"{lat}, {lon}", timeout=10)
        return location.address if location else "Address not found"
    except:
        return "Address Fetch Timeout (Network Issue)"

# AUTOMATIC NAME FETCH FROM LINK
query_params = st.query_params
url_name = query_params.get("name", "").replace("_", " ")

# --- APP INTERFACE ---
st.title("📍 Field Service Portal")
st.write(f"Service Date: {datetime.now().strftime('%d %B %Y')}")

# Tabs
tab1, tab2 = st.tabs(["🔒 Service Check-In", "⚙️ Service Admin Panel"])

# ================= TAB 1: 100% AUTOMATIC EMPLOYEE PANEL =================
with tab1:
    if not url_name:
        st.error("⚠️ Invalid Link! Please open the personalized link sent via SMS.")
    else:
        st.markdown(f"### Processing Verification for: **{url_name}**")
        
        loc = get_geolocation()
        
        if "verified_user" not in st.session_state:
            st.session_state.verified_user = False
            
        if not loc or 'coords' not in loc:
            st.info("🔄 Requesting secure GPS device signal... Please wait a second.")
        elif not st.session_state.verified_user:
            try:
                lat = loc['coords']['latitude']
                lon = loc['coords']['longitude']
                
                with st.spinner("⚡ Auto-verifying your field location..."):
                    readable_address = get_text_address(lat, lon)
                    maps_link = f"https://www.google.com/maps?q={lat},{lon}"
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    new_data = pd.DataFrame([[timestamp, url_name, readable_address, maps_link]], 
                                            columns=["Timestamp", "Employee Name", "Text Address", "Google Maps Link"])
                    new_data.to_csv(DATA_FILE, mode='a', header=False, index=False)
                    
                    st.session_state.verified_user = True
                    st.rerun()
            except Exception as e:
                st.error("⚠️ Auto-fetch response interrupted. Please refresh this page.")

        if st.session_state.verified_user:
            st.success(f"✅ Attendance & Location Verified Successfully for {url_name}!")
            st.balloons()

# ================= TAB 2: SECURE ADMIN PANEL =================
with tab2:
    st.subheader("🔒 Secure Service Monitoring")
    admin_pass = st.text_input("Enter Service Admin Password", type="password")
    
    if admin_pass == PASSWORD:
        st.success("Access Granted!")
        
        df_records = pd.read_csv(DATA_FILE)
        total_checks = len(df_records)
        unique_emps = df_records["Employee Name"].nunique() if total_checks > 0 else 0
        
        col1, col2 = st.columns(2)
        col1.metric("Total Service Check-Ins", total_checks)
        col2.metric("Active Employees on Field", unique_emps)
        
        st.markdown("### Live Service Records")
        
        st.dataframe(
            df_records.iloc[::-1], 
            use_container_width=True,
            column_config={
                "Google Maps Link": st.column_config.LinkColumn("Google Maps Link", display_text="Open Map 🗺️")
            }
        )
        
        csv = df_records.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Service Report",
            data=csv,
            file_name=f"Service_Report_{datetime.now().strftime('%Y-%m-%d')}.csv",
            mime='text/csv',
        )
    elif admin_pass != "":
        st.error("❌ Wrong Password! Access Denied.")
