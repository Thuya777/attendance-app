import streamlit as st
import pandas as pd
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ၁။ Google Sheet ချိတ်ဆက်မှု
if "gcp_service_account" in st.secrets:
    info = st.secrets["gcp_service_account"]
    credentials = service_account.Credentials.from_service_account_info(info)
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()

SPREADSHEET_ID = "1Lnh_L7v7vDs-6WRosRlKXzNSoqANljgAKRc5VvAIpFs"

# Sidebar Menu
st.sidebar.title("ရုံးလုပ်ငန်းသုံး App")
menu = st.sidebar.radio("သွားလိုသည့် အပိုင်းကို ရွေးပါ", ["ရုံးတက်/ထွက်", "ဝန်ထမ်းအသစ်ထည့်ရန်", "ခွင့်တိုင်ရန်", "Admin (စည်းကမ်းပြင်ရန်)"])

# --- ၁။ ရုံးတက်/ထွက် အပိုင်း ---
if menu == "ရုံးတက်/ထွက်":
    st.header("🏥 ဝန်ထမ်းရုံးတက်/ထွက် မှတ်တမ်း")
    res = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Employees!A:A").execute()
    names = [row[0] for row in res.get('values', []) if row]
    selected_name = st.selectbox("သင့်အမည်ကို ရွေးပါ", ["-- ရွေးရန် --"] + names)
    if selected_name != "-- ရွေးရန် --":
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Check In", use_container_width=True):
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sheet.values().append(spreadsheetId=SPREADSHEET_ID, range="Attendance!A:C", 
                                      valueInputOption="USER_ENTERED", body={'values': [[selected_name, now, "In"]]}).execute()
                st.success(f"{selected_name} ရုံးတက်ချိန် မှတ်သားပြီး")
        with col2:
            if st.button("❌ Check Out", use_container_width=True):
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sheet.values().append(spreadsheetId=SPREADSHEET_ID, range="Attendance!A:C", 
                                      valueInputOption="USER_ENTERED", body={'values': [[selected_name, now, "Out"]]}).execute()
                st.warning(f"{selected_name} ရုံးထွက်ချိန် မှတ်သားပြီး")

# --- ၂။ ဝန်ထမ်းအသစ်ထည့်ရန် အပိုင်း ---
elif menu == "ဝန်ထမ်းအသစ်ထည့်ရန်":
    st.header("👤 ဝန်ထမ်းအမည်အသစ် ထည့်သွင်းရန်")
    new_name = st.text_input("အမည်အသစ် ရိုက်ထည့်ပါ")
    if st.button("အမည်သွင်းမည်"):
        if new_name:
            sheet.values().append(spreadsheetId=SPREADSHEET_ID, range="Employees!A:A", 
                                  valueInputOption="USER_ENTERED", body={'values': [[new_name]]}).execute()
            st.success(f"'{new_name}' ကို ထည့်သွင်းပြီးပါပြီ")

# --- ၃။ ခွင့်တိုင်ရန် အပိုင်း ---
elif menu == "ခွင့်တိုင်ရန်":
    st.header("📝 ခွင့်တိုင်ကြားခြင်း")
    sett = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Settings!A1").execute()
    rules = sett.get('values', [["စည်းကမ်းချက်များ မသတ်မှတ်ရသေးပါ။"]])[0][0]
    st.info(f"### ⚠️ ခွင့်စည်းကမ်းချက်များ\n{rules}")
    agree = st.checkbox("ကျွန်ုပ်သည် စည်းကမ်းချက်များကို ဖတ်ရှုနားလည်ပြီး ဖြစ်ပါသည်။")
    if agree:
        res = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Employees!A:A").execute()
        names = [row[0] for row in res.get('values', []) if row]
        name = st.selectbox("အမည်ရွေးပါ", names)
        l_type = st.selectbox("ခွင့်အမျိုးအစား", ["ရှောင်တခင်ခွင့်", "ဆေးခွင့်", "နာရေးခွင့်"])
        reason = st.text_area("အကြောင်းပြချက်")
        if st.button("ခွင့်တင်မည်"):
            date = datetime.now().strftime("%Y-%m-%d")
            sheet.values().append(spreadsheetId=SPREADSHEET_ID, range="Leave_Requests!A:D", 
                                  valueInputOption="USER_ENTERED", body={'values': [[name, l_type, reason, date]]}).execute()
            st.success("ခွင့်တိုင်ကြားမှု အောင်မြင်ပါသည်။")

# --- ၄။ Admin အပိုင်း (စည်းကမ်းပြင်ရန်) ---
elif menu == "Admin (စည်းကမ်းပြင်ရန်)":
    st.header("⚙️ ခွင့်စည်းကမ်းချက်များ ပြင်ဆင်ရန်")
    current_sett = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Settings!A1").execute()
    current_rules = current_sett.get('values', [[""]])[0][0]
    new_rules = st.text_area("စည်းကမ်းချက်များကို ဤနေရာတွင် ပြင်ပါ", value=current_rules, height=200)
    if st.button("စည်းကမ်းချက် အပ်ဒိတ်လုပ်မည်"):
        sheet.values().update(spreadsheetId=SPREADSHEET_ID, range="Settings!A1", 
                              valueInputOption="USER_ENTERED", body={'values': [[new_rules]]}).execute()
        st.success("စည်းကမ်းချက်များကို အောင်မြင်စွာ ပြောင်းလဲပြီးပါပြီ။")
