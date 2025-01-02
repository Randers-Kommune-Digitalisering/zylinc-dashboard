import streamlit as st
from utils.logo import get_logo
from streamlit_option_menu import option_menu
from page.duration import show_conversation_duration
from page.queue_time import show_queue_time
from page.live import display_live_data
from page.upload import upload_csv_file
from page.conversation_calls import show_conversation_call

st.set_page_config(page_title="IT-Support", page_icon="assets/favicon.ico", layout="wide")

with st.sidebar:
    st.sidebar.markdown(get_logo(), unsafe_allow_html=True)
    selected = option_menu(
        "IT Support Zylinc",
        ["Live Data", 'Upload CSV-fil', 'Varighed af samtale', 'Resultat af opkald', 'Ventetid pr opkald', 'Antal af samtaler'],
        icons=['house', 'cloud-upload'],
        default_index=0
    )

if selected == "Live Data":
    display_live_data()
elif selected == 'Varighed af samtale':
    show_conversation_duration()
elif selected == 'Antal af samtaler':
    show_conversation_call()
elif selected == 'Resultat af opkald':
    st.write("Resultat af opkald")
elif selected == 'Ventetid pr opkald':
    show_queue_time()
elif selected == 'Upload CSV-fil':
    upload_csv_file()
