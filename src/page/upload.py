import pandas as pd
import streamlit as st
from utils.data import load_and_process_data


def upload_csv_file():
    uploaded_file = st.file_uploader("Upload CSV fil", type=['csv'], key='file')

    if uploaded_file is not None:
        try:
            historical_data = pd.read_csv(uploaded_file, sep=',')
            processed_data = load_and_process_data(historical_data)
            st.session_state['historical_data'] = processed_data
            st.success("CSV filen med Zylinc data er uploadet")
        except Exception as e:
            st.error(f"Fejl ved indlæsning af fil: {e}")
            st.stop()
    else:
        st.warning("Upload venligst en CSV fil for at fortsætte.")
