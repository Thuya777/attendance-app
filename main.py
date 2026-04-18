import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os

# Page config
st.set_page_config(page_title="Staff Attendance System", layout="wide")

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)

# Open the Google Sheet
sheet = client.open("Attendance_DB")

# Get settings and staff list
try:
    conf_sheet = sheet.worksheet("Settings")
    staff_data = conf_sheet.get_all_records()
    staff_list = [row['Name'] for row in staff_data]
    admin_password = str(staff_data[0]['AdminPassword'])
except Exception as e:
    st.error(f"Error loading settings: {e}")
    staff_list = ["Staff A", "Staff B"] # Fallback
    admin_password = "1234"

# Attendance Sheet
att_sheet = sheet.worksheet("Attendance")
leave_sheet = sheet.worksheet("Leave_Requests")

st.title("Attendance & Leave Management")

menu = st.sidebar.selectbox("Main Menu", ["ရုံးတက်/ဆင်း လုပ်ရန်", "ခွင့်တိုင်ရန်", "Admin Panel"])

if menu == "ရုံးတက်/ဆင်း လုပ်ရန်":
    st.header("📸 ဝန်ထမ်း ရုံးတက်/ဆင်း လုပ်ပေးရန်")
    name = st.selectbox("ဝန်ထမ်းအမည် ရွေးပါ", staff_list)
    status = st.radio("အမျိုးအစား", ["ရုံးတက် (Check-In)", "ရုံးဆင်း (Check-Out)"])
    
    img_file = st.camera_input("ဓာတ်ပုံရိုက်ပါ")
    
    if st.button("Submit"):
        if img_file:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            att_sheet.append_row([now, name, status, "Photo Captured"])
            st.success(f"{name} အတွက် {status} လုပ်ဆောင်ချက် အောင်မြင်ပါသည်!")
        else:
            st.warning("ကျေးဇူးပြု၍ ဓာတ်ပုံအရင်ရိုက်ပါ!")

elif menu == "ခွင့်တိုင်ရန်":
    st.header("📝 ခွင့်တိုင်ကြားလွှာ")
    with st.form("leave_form"):
        l_name = st.selectbox("အမည်", staff_list)
        l_type = st.selectbox("ခွင့်အမျိုးအစား", ["ရှောင်တခင်ခွင့်", "ဆေးခွင့်", "လုပ်သက်ခွင့်"])
        l_reason = st.text_area("အကြောင်းပြချက်")
        if st.form_submit_button("ခွင့်တင်မည်"):
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            leave_sheet.append_row([now, l_name, l_type, l_reason, "Pending"])
            st.success("ခွင့်တင်ခြင်း အောင်မြင်ပါသည်။")

elif menu == "Admin Panel":
    pwd = st.sidebar.text_input("Admin Password ရိုက်ထည့်ပါ", type="password")
    if pwd == admin_password:
        st.sidebar.success("Admin Access Granted")
        tab1, tab2 = st.tabs(["Attendance Data", "Leave Requests"])
        with tab1:
            df = pd.DataFrame(att_sheet.get_all_records())
            st.dataframe(df)
        with tab2:
            ldf = pd.DataFrame(leave_sheet.get_all_records())
            st.dataframe(ldf)
    else:
        st.sidebar.error("Password မှားယွင်းနေပါသည်။")