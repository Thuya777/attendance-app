import streamlit as st
import pandas as pd
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
import PIL.Image as Image

# ၁။ Google Sheet ချိတ်ဆက်မှု
if "gcp_service_account" in st.secrets:
    info = st.secrets["gcp_service_account"]
    credentials = service_account.Credentials.from_service_account_info(info)
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()

SPREADSHEET_ID = "1Lnh_L7v7vDs-6WRosRlKXzNSoqANljgAKRc5VvAIpFs"

# Sidebar Menu
st.sidebar.title("🏢 ရုံးလုပ်ငန်းသုံး App")
menu = st.sidebar.radio("သွားလိုသည့် အပိုင်းကို ရွေးပါ", ["ရုံးတက်/ထွက်", "ခွင့်တိုင်ရန်", "Admin Panel (စီမံခန့်ခွဲသူ)"])

# --- ၁။ ရုံးတက်/ထွက် အပိုင်း (မျက်နှာစစ်ဆေးခြင်း စနစ်ပါဝင်သည်) ---
if menu == "ရုံးတက်/ထွက်":
    st.header("🏥 ဝန်ထမ်းရုံးတက်/ထွက် မှတ်တမ်း")
    
    # ဝန်ထမ်းအမည်နှင့် Photo ID ကို တွဲယူခြင်း
    res = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Employees!A:B").execute()
    rows = res.get('values', [])
    
    # နာမည်စာရင်းထုတ်ယူခြင်း
    names_data = {row[0]: (row[1] if len(row) > 1 else None) for row in rows[1:] if row}
    selected_name = st.selectbox("သင့်အမည်ကို ရွေးပါ", ["-- ရွေးရန် --"] + list(names_data.keys()))

    if selected_name != "-- ရွေးရန် --":
        photo_id = names_data[selected_name]
        
        # ဝန်ထမ်းပုံ ရှိလျှင် ပြသရန်
        if photo_id:
            img_url = f"https://drive.google.com/thumbnail?id={photo_id}&sz=w300"
            st.image(img_url, caption=f"{selected_name} ၏ မှတ်တမ်းဝင်ဓာတ်ပုံ", width=150)
        else:
            st.warning("ဝန်ထမ်းဓာတ်ပုံ မရှိသေးပါ။")

        st.subheader("📸 မျက်နှာစစ်ဆေးခြင်း")
        st.info("ခလုတ်မနှိပ်မီ ရှေ့ကင်မရာဖြင့် ဓာတ်ပုံရိုက်ပြီး မျက်နှာအတည်ပြုပေးပါ။")
        
        # ကင်မရာ ဖွင့်ခြင်း
        cam_photo = st.camera_input("မျက်နှာ အတည်ပြုရန်")

        if cam_photo:
            st.success("✅ မျက်နှာရိုက်ကူးမှု အောင်မြင်သည်။ (မှတ်ချက် - AI Verification စနစ်ကို Server တွင် သတ်မှတ်ရန် လိုအပ်ပါသည်)")
            
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

# --- ၂။ ခွင့်တိုင်ရန် အပိုင်း ---
elif menu == "ခွင့်တိုင်ရန်":
    st.header("📝 ခွင့်တိုင်ကြားခြင်း")
    sett = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Settings!A1").execute()
    rules = sett.get('values', [["စည်းကမ်းချက်များ မသတ်မှတ်ရသေးပါ။"]])[0][0]
    st.info(f"### ⚠️ ခွင့်စည်းကမ်းချက်များ\n{rules}")
    
    agree = st.checkbox("ကျွန်ုပ်သည် စည်းကမ်းချက်များကို ဖတ်ရှုနားလည်ပြီး ဖြစ်ပါသည်။")
    if agree:
        res = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Employees!A:A").execute()
        names = [row[0] for row in res.get('values', []) if row[0] != "Name"]
        name = st.selectbox("အမည်ရွေးပါ", names)
        l_type = st.selectbox("ခွင့်အမျိုးအစား", ["ရှောင်တခင်ခွင့်", "ဆေးခွင့်", "နာရေးခွင့်"])
        reason = st.text_area("အကြောင်းပြချက်")
        if st.button("ခွင့်တင်မည်"):
            date = datetime.now().strftime("%Y-%m-%d")
            sheet.values().append(spreadsheetId=SPREADSHEET_ID, range="Leave_Requests!A:D", 
                                  valueInputOption="USER_ENTERED", body={'values': [[name, l_type, reason, date]]}).execute()
            st.success("ခွင့်တိုင်ကြားမှု အောင်မြင်ပါသည်။")

# --- ၃။ Admin Panel (လုံခြုံရေး Password ပါဝင်သည်) ---
elif menu == "Admin Panel (စီမံခန့်ခွဲသူ)":
    st.header("🔐 Admin Panel")
    password = st.text_input("Admin Password ရိုက်ထည့်ပါ", type="password")
    
           # --- try ဆိုတာကို သီးသန့်စာကြောင်းအနေနဲ့ အစမှာထားပါ ---
    try:
    # Settings sheet ထဲက B1 အကွက် (Password) ကို ဖတ်ခြင်း
    conf_sheet = sheet.worksheet("Settings")
    correct_password = conf_sheet.acell('B1').value
    except Exception as e:
    # တစ်ခုခု မှားယွင်းခဲ့ရင် Backup အနေနဲ့ 1234 ကို သုံးမယ်
    correct_password = "1234"

    if password == correct_password:  # Password ကို ဤနေရာတွင် ပြောင်းနိုင်သည်
        st.success("Admin Login အောင်မြင်သည်။")
        tab1, tab2 = st.tabs(["ဝန်ထမ်းအသစ်/ဓာတ်ပုံပြင်ရန်", "စည်းကမ်းချက်ပြင်ရန်"])
        
        with tab1:
            st.subheader("👤 ဝန်ထမ်းစီမံခြင်း")
            new_name = st.text_input("ဝန်ထမ်းအမည်သစ်")
            new_photo_id = st.text_input("Google Drive Photo ID (အရှည်ကြီး)")
            
            if st.button("ဝန်ထမ်းအသစ် သိမ်းမည်"):
                if new_name and new_photo_id:
                    sheet.values().append(spreadsheetId=SPREADSHEET_ID, range="Employees!A:B", 
                                          valueInputOption="USER_ENTERED", body={'values': [[new_name, new_photo_id]]}).execute()
                    st.success(f"'{new_name}' ကို ထည့်သွင်းပြီးပါပြီ။")
                else:
                    st.error("အချက်အလက် အကုန်ဖြည့်ပါ။")
                    
        with tab2:
            st.subheader("⚙️ စည်းကမ်းချက်များ ပြင်ဆင်ရန်")
            current_sett = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Settings!A1").execute()
            current_rules = current_sett.get('values', [[""]])[0][0]
            new_rules = st.text_area("ပြင်ဆင်ရန်", value=current_rules, height=200)
            if st.button("Update Rules"):
                sheet.values().update(spreadsheetId=SPREADSHEET_ID, range="Settings!A1", 
                                      valueInputOption="USER_ENTERED", body={'values': [[new_rules]]}).execute()
                st.success("စည်းကမ်းချက်များ ပြောင်းလဲပြီးပါပြီ။")
    elif password != "":
        st.error("Password မှားယွင်းနေပါသည်။")
