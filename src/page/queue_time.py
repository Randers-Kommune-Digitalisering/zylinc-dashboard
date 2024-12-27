import streamlit as st
import streamlit_antd_components as sac
from datetime import datetime
import altair as alt
from utils.data import load_and_process_data
from utils.time import convert_minutes_to_hms
from utils.config import CSV_PATH
import pandas as pd


def show_queue_time():
    col_1 = st.columns([1])[0]

    with col_1:
        content_tabs = sac.tabs([
            sac.TabsItem('Dag', tag='Dag'),
        ], color='dark', size='md', position='top', align='start', use_container_width=True)

    historical_data = load_and_process_data(CSV_PATH)

    if content_tabs == 'Dag':

        unique_dates = historical_data['StartTimeDenmark'].dt.date.unique()
        selected_date = st.date_input("Vælg en dato", min_value=min(unique_dates), max_value=max(unique_dates), key='date_input')

        historical_data_today = historical_data[(historical_data['StartTimeDenmark'].dt.date == selected_date) &
                                                (historical_data['StartTimeDenmark'].dt.time.between(datetime.strptime('06:00', '%H:%M').time(), datetime.strptime('16:00', '%H:%M').time()))]

        avg_wait_time_today = historical_data_today['QueueDurationMinutes'].mean()

        avg_wait_time_today = 0 if pd.isna(avg_wait_time_today) else avg_wait_time_today

        st.metric(label="Gennemsnitlig ventetid i dag", value=convert_minutes_to_hms(avg_wait_time_today))

        queue_data = historical_data_today[historical_data_today['ConversationEventType'].isin(['JoinedQueue', 'LeftQueue'])]

        queue_data['QueueDurationHMS'] = queue_data['QueueDurationMinutes'].apply(convert_minutes_to_hms)

        st.write("## Ventetid i kø (Dag)")
        chart = alt.Chart(queue_data).mark_bar().encode(
            x=alt.X('StartTimeDenmark:T', title='Tidspunkt', axis=alt.Axis(format='%Y-%m-%d %H:%M')),
            y=alt.Y('QueueDurationMinutes:Q', title='Ventetid (minutter)'),
            color=alt.Color('QueueName:N', title='Kø'),
            tooltip=[alt.Tooltip('StartTimeDenmark:T', title='Tidspunkt', format='%Y-%m-%d %H:%M'), alt.Tooltip('QueueDurationHMS:N', title='Ventetid'), alt.Tooltip('QueueName:N', title='Kø')]
        ).properties(
            height=500
        )
        st.altair_chart(chart, use_container_width=True)


show_queue_time()
