import streamlit as st
from utils.logo import get_logo
from streamlit_option_menu import option_menu
from page.varighed import show_conversation_duration
from page.queue_time import show_queue_time

with st.sidebar:
    st.sidebar.markdown(get_logo(), unsafe_allow_html=True)
    selected = option_menu(
        "IT Support Zylinc",
        ["Live Data", 'Varighed af samtale', 'Antal af samtaler', 'Resultat af opkald', 'Ventetid pr opkald'],
        icons=['house'],
        default_index=0
    )

if selected == "Live Data":
    st.write("Se Live Data for IT Support Zylinc")
elif selected == 'Varighed af samtale':
    show_conversation_duration()
elif selected == 'Antal af samtaler':
    st.write("Antal af samtaler")
elif selected == 'Resultat af opkald':
    st.write("Resultat af opkald")
elif selected == 'Ventetid pr opkald':
    show_queue_time()
