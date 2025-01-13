import streamlit as st
from utils.logo import get_logo
from streamlit_option_menu import option_menu
from page.conversation_duration import show_conversation_duration
from page.conversation_queue_time import show_queue_time
from page.live import display_live_data
from page.upload import upload_csv_file, load_csv_file
from page.conversation_calls import show_conversation_call
from page.conversation_result import show_conversation_result
from page.conversation_load import show_conversation_load
from streamlit_keycloak import login

from utils.config import KEYCLOAK_URL, KEYCLOAK_REALM, KEYCLOAK_CLIENT_ID

st.set_page_config(page_title="IT-Support", page_icon="assets/favicon.ico", layout="wide")

keycloak = login(
    url=KEYCLOAK_URL,
    realm=KEYCLOAK_REALM,
    client_id=KEYCLOAK_CLIENT_ID
)

if keycloak.authenticated:
    load_csv_file()

    with st.sidebar:
        st.sidebar.markdown(get_logo(), unsafe_allow_html=True)
        selected = option_menu(
            "IT Support Zylinc",
            ["Live Data", 'Hent historisk data', 'Varighed af samtale', 'Resultat af opkald', 'Ventetid pr opkald', 'Antal af samtaler', 'Belastning'],
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
        show_conversation_result()
    elif selected == 'Ventetid pr opkald':
        show_queue_time()
    elif selected == 'Hent historisk data':
        upload_csv_file()
    elif selected == 'Belastning':
        show_conversation_load()
else:
    st.markdown('''<span style="color:red">Du er ikke logget ind med en gyldig Randers konto</span>''', unsafe_allow_html=True)
