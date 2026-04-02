import streamlit as st
import pandas as pd
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ၁။ Google Sheet ချိတ်ဆက်မှု အပိုင်း
if "gcp_service_account" in st.secrets:
    info = st.secrets["gcp_service_account"]
    credentials = service_account.Credentials.from_service_account_info(info)
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()

# ၂။ သင့်ရဲ့ Google Sheet ID ဖြစ်ပါတယ်
SPREADSHEET_ID = "1Lnh_L7v7VDs-6WRosRIKXznSoqANLjgAKRNzQ5pX37E"
RANGE_NAME = "Employees!A:C" # သင့် Sheet နာမည်ကို Employees လို့ ပြင်ထားပေးပါ

st.title("🏥 ဝန်ထမ်းရုံးတက်/ထွက် မှတ်တမ်း")

staff_list = ["မောင်မောင်", "ကျော်ကျော်", "အေးအေး", "လှလှ", "မြမြ"]
selected_name = st.selectbox("သင့်အမည်ကို ရွေးချယ်ပါ", ["-- ရွေးရန် --"] + staff_list)

if selected_name != "-- ရွေးရန် --":
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ ရုံးတက် (Check In)", use_container_width=True):
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            values = [[selected_name, now, "In"]]
            body = {'values': values}
            sheet.values().append(
                spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME,
                valueInputOption="USER_ENTERED", body=body).execute()
            st.success(f"{selected_name} ရုံးတက်ချိန် မှတ်သားပြီးပါပြီ။")

    with col2:
        if st.button("❌ ရုံးထွက် (Check Out)", use_container_width=True):
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            values = [[selected_name, now, "Out"]]
            body = {'values': values}
            sheet.values().append(
                spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME,
                valueInputOption="USER_ENTERED", body=body).execute()
            st.warning(f"{selected_name} ရုံးထွက်ချိန် မှတ်သားပြီးပါပြီ။")
