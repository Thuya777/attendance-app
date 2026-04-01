import streamlit as st
import pandas as pd
from datetime import datetime
import os
# ဖိုင်အမည် သတ်မှတ်ခြင်း
FILE_NAME = 'office_attendance.csv'
st.title("🏢 ဝန်ထမ်းရုံးတက်/ထွက် မှတ်တမ်း")
staff_list = ["မောင်မောင်", "ကျော်ကျော်", "အေးအေး", "လှလှ", "မြမြ"]
selected_name = st.selectbox("သင့်အမည်ကို ရွေးချယ်ပါ", ["-- ရွေးရန် --"] + staff_list)
if selected_name != "-- ရွေးရန် --":
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ ရုံးတက် (Check In)", use_container_width=True):
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
            new_data = pd.DataFrame([[selected_name, dt_string, "In"]], columns=['Name', 'Time', 'Status'])
            new_data.to_csv(FILE_NAME, mode='a', index=False, header=not os.path.exists(FILE_NAME))
            st.success(f"{selected_name} ရုံးတက်ချိန် မှတ်သားပြီးပါပြီ။")
    with col2:
        if st.button("❌ ရုံးထွက် (Check Out)", use_container_width=True):
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
            new_data = pd.DataFrame([[selected_name, dt_string, "Out"]], columns=['Name', 'Time', 'Status'])
            new_data.to_csv(FILE_NAME, mode='a', index=False, header=not os.path.exists(FILE_NAME))
            st.warning(f"{selected_name} ရုံးထွက်ချိန် မှတ်သားပြီးပါပြီ။")