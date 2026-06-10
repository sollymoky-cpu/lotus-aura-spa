import streamlit as st
import pandas as pd
from datetime import datetime
import os
from geopy.geocoders import Nominatim
from streamlit_js_eval import get_geolocation

# Page Configuration
st.set_page_config(page_title="Field Service Portal", layout="centered")

DATA_FILE = "service_records.csv"
PASSWORD = "Sanjay@Admin2026"

if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Timestamp", "Employee Name", "Text Address", "Google Maps Link"])
    df.to_csv(DATA_FILE, index=False)

def get_text_address(lat, lon):
    try:
        geolocator = Nominatim(user_agent="field_service_enterprise_portal")
        location = geolocator.reverse(f"{lat}, {lon}", timeout=10)
        return location.address if location else "Address not found"
    except:
        return "Network Error"

query_params = st.query_params
url_name = query_params.get("name", "").replace("_", " ")

st.title("💼 Field Attendance System")

tab1, tab2 = st.tabs(["🔒 Daily Check-In", "⚙️ Admin Panel"])

# ================= EMPLOYEE PANEL =================
with tab1:
    if not url_name:
        st.error("⚠️ Invalid Link!")
    else:
        st.markdown(f"### Namaste, **{url_name}**")
        st.write("Aaj ki duty chalu karne ke liye niche diye gaye green button ko dabayein.")
        
        if "verified_user" not in st.session_state:
            st.session_state.verified_user = False

        # CSS for Big Smooth Green Button
        st.markdown("""
            <style>
            div.stButton > button:first-child {
                background-color: #4CAF50;
                color: white;
                font-size: 22px;
                font-weight: bold;
                padding: 18px 30px;
                border-radius: 12px;
                border: none;
                width: 100%;
                box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
                transition: 0.3s;
            }
            div.stButton > button:first-child:hover {
                background-color: #45a049;
                color: white;
            }
            </style>
        """, unsafe_allow_html=True)

        # Aapke mutabik bilkul simple button text
        trigger_gps = st.button("Ha me field par hu, Kaam chalu 👍")

        if trigger_gps and not st.session_state.verified_user:
            with st.spinner("🔄 Processing Check-In... (Kripya screen par ALLOW/OK par click karein)"):
                loc = get_geolocation()
                
                if loc and 'coords' in loc:
                    try:
                        lat = loc['coords']['latitude']
                        lon = loc['coords']['longitude']
                        
                        readable_address = get_text_address(lat, lon)
                        maps_link = f"https://www.google.com/maps?q={lat},{lon}"
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        new_data = pd.DataFrame([[timestamp, url_name, readable_address, maps_link]], 
                                                columns=["Timestamp", "Employee Name", "Text Address", "Google Maps Link"])
                        new_data.to_csv(DATA_FILE, mode='a', header=False, index=False)
                        
                        st.session_state.verified_user = True
                        st.rerun()
                    except Exception as e:
                        st.error("⚠️ Server Busy. Please click button again.")
                else:
                    st.info("🔄 Attendance process karne ke liye, screen par aane wale option ko 'Allow' karke button dubaara dabayein.")

        if st.session_state.verified_user:
            st.success(f"🎉 Thank you! Aapki aaj ki attendance lag gayi hai.")
            st.balloons()

# ================= ADMIN PANEL =================
with tab2:
    st.subheader("🔒 Secure Service Monitoring")
    admin_pass = st.text_input("Enter Password", type="password")
    
    if admin_pass == PASSWORD:
        st.success("Access Granted!")
        df_records = pd.read_csv(DATA_FILE)
        st.dataframe(
            df_records.iloc[::-1], 
            use_container_width=True,
            column_config={"Google Maps Link": st.column_config.LinkColumn("Google Maps Link", display_text="Open Map 🗺️")}
        )
