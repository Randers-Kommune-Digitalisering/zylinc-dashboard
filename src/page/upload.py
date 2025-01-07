import pandas as pd
import streamlit as st
import os
from utils.data import load_and_process_data
from utils.config import UPLOAD_DIR


def load_csv_file():
    upload_dir = UPLOAD_DIR
    file_path = os.path.join(upload_dir, "uploaded_file.csv")

    if os.path.exists(file_path):
        try:
            historical_data = pd.read_csv(file_path, sep=',')
            processed_data = load_and_process_data(historical_data)
            st.session_state['historical_data'] = processed_data
        except Exception as e:
            st.error(f"Fejl ved indlæsning af fil: {e}")
    else:
        st.warning("Ingen tidligere CSV fil fundet. Upload venligst en CSV fil.")


def upload_csv_file():
    upload_dir = UPLOAD_DIR
    file_path = os.path.join(upload_dir, "uploaded_file.csv")

    uploaded_file = st.file_uploader("Upload og overskriv forrige CSV fil med nyt data", type=['csv'], key='file')

    if uploaded_file is not None:
        try:
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)

            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            historical_data = pd.read_csv(file_path, sep=',')
            processed_data = load_and_process_data(historical_data)
            st.session_state['historical_data'] = processed_data
            st.success("CSV filen med Zylinc data er uploadet og gemt")
        except Exception as e:
            st.error(f"Fejl ved indlæsning af fil: {e}")
            st.stop()
