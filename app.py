import streamlit as st
import pandas as pd
from datetime import datetime
import os
from geopy.geocoders import Nominatim
from streamlit_js_eval import get_geolocation

# Page Configuration - Standardized Branding
st.set_page_config(page_title="Field Service Portal", layout="centered")

DATA_FILE = "service_records.csv"
PASSWORD = "Service@Admin123"  # Standard secure password for admin panel

# Initialize CSV Database
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Timestamp", "Employee Name", "Text Address", "Google Maps Link"])
    df.to_csv(DATA_FILE, index=False)

# Reverse Geocoding Function (Coordinates se Text Address nikalna)
def get_text_address(lat, lon):
    try:
        geolocator = Nominatim(user_agent="field_service_enterprise_portal")
        location = geolocator.reverse(f"{lat}, {lon}", timeout=10)
        return location.address if location else "Address not found"
    except:
        return "Address Fetch Timeout (Network Issue)"

# AUTOMATIC NAME FETCH FROM LINK (URL Query Parameters)
query_params = st.query_params
url_name = query_params.get("name", "").replace("_", " ")

# --- APP INTERFACE ---
st.title("📍 Field Service Portal")
st.write(f"Service Date: {datetime.now().strftime('%d %B %Y')}")

# Tabs - Service Dashboard and Service Check-In
tab1, tab2 = st.tabs(["🔒 Service Check-In", "⚙️ Service Admin Panel"])

# ================= TAB 1: EMPLOYEE PANEL =================
with tab1:
    st.subheader("Field Service Verification")
    
    if url_name:
        st.markdown(f"Welcome, **{url_name}** 👋")
        emp_name = url_name
    else:
        emp_name = st.text_input("Enter Your Full Name", placeholder="e.g. Amit Sharma")
    
    # Location catch karne ke liye hidden component
    loc = get_geolocation()
    
    if st.button("🚀 Verify & Submit Service Location", type="primary"):
        if not emp_name.strip():
            st.error("⚠️ Please enter your name first!")
        # ERROR PROTECTION: Check agar loc null hai ya 'coords' nahi mila
        elif not loc or 'coords' not in loc:
            st.warning("🔄 GPS Signal weak hai ya Permission load ho rahi hai. Kripya 2 second ruk kar dubara button dabayein.")
        else:
            try:
                lat = loc['coords']['latitude']
                lon = loc['coords']['longitude']
                
                with st.spinner("⚡ Fetching exact pinpoint service address..."):
                    readable_address = get_text_address(lat, lon)
                    maps_link = f"https://maps.google.com/?q={lat},{lon}"
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Save to CSV background me
                    new_data = pd.DataFrame([[timestamp, emp_name, readable_address, maps_link]], 
                                            columns=["Timestamp", "Employee Name", "Text Address", "Google Maps Link"])
                    new_data.to_csv(DATA_FILE, mode='a', header=False, index=False)
                    
                    st.success(f"✅ Thank you {emp_name}! Your service location has been verified.")
                    st.balloons()
            except Exception as e:
                st.error("⚠️ Browser se response nahi mila. Kripya page refresh karke dubara try karein.")

# ================= TAB 2: ADMIN PANEL =================
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
        st.dataframe(df_records.iloc[::-1], use_container_width=True)
        
        csv = df_records.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Service Report",
            data=csv,
            file_name=f"Service_Report_{datetime.now().strftime('%Y-%m-%d')}.csv",
            mime='text/csv',
        )
    elif admin_pass != "":
        st.error("❌ Wrong Password! Access Denied.")