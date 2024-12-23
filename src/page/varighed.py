import streamlit as st
import streamlit_antd_components as sac
from datetime import datetime
import altair as alt
from utils.data import load_and_process_data
from utils.config import CSV_PATH
import pandas as pd


def show_conversation_duration():
    col_1 = st.columns([1])[0]

    with col_1:
        content_tabs = sac.tabs([
            sac.TabsItem('Dag', tag='Dag'),
            sac.TabsItem('Uge', tag='Uge'),
            sac.TabsItem('Måned', tag='Måned'),
            sac.TabsItem('Kvartal', tag='Kvartal'),
        ], color='dark', size='md', position='top', align='start', use_container_width=True)

    historical_data = load_and_process_data(CSV_PATH)

    if content_tabs == 'Dag':
        unique_dates = historical_data['StartTimeDenmark'].dt.date.unique()
        selected_date = st.date_input("Vælg en dato", min_value=min(unique_dates), max_value=max(unique_dates), key='date_input')

        historical_data_today = historical_data[(historical_data['StartTimeDenmark'].dt.date == selected_date) &
                                                (historical_data['StartTimeDenmark'].dt.time.between(datetime.strptime('06:00', '%H:%M').time(), datetime.strptime('16:00', '%H:%M').time()))]

        yesterday = selected_date - pd.Timedelta(days=1)
        historical_data_yesterday = historical_data[(historical_data['StartTimeDenmark'].dt.date == yesterday) &
                                                    (historical_data['StartTimeDenmark'].dt.time.between(datetime.strptime('06:00', '%H:%M').time(), datetime.strptime('16:00', '%H:%M').time()))]

        answered_calls_today = historical_data_today[historical_data_today['Result'] == 'Answered'].shape[0]
        missed_calls_today = historical_data_today[historical_data_today['Result'] == 'Missed'].shape[0]

        answered_calls_yesterday = historical_data_yesterday[historical_data_yesterday['Result'] == 'Answered'].shape[0]
        missed_calls_yesterday = historical_data_yesterday[historical_data_yesterday['Result'] == 'Missed'].shape[0]

        delta_answered_calls = answered_calls_today - answered_calls_yesterday
        delta_missed_calls = missed_calls_today - missed_calls_yesterday

        st.metric(label="Antal besvarede opkald", value=answered_calls_today, delta=delta_answered_calls)
        st.metric(label="Antal mistede opkald", value=missed_calls_today, delta=delta_missed_calls)

        chart_data = historical_data_today[['StartTimeDenmark', 'DurationMinutes', 'AgentDisplayName']]

        st.write("## Varighed af samtale(Dag)")
        chart = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('StartTimeDenmark:T', title='Tidspunkt', axis=alt.Axis(format='%Y-%m-%d %H:%M')),
            y=alt.Y('DurationMinutes:Q', title='Varighed (minutter)'),
            color=alt.Color('AgentDisplayName:N', title='Agent'),
            tooltip=[alt.Tooltip('StartTimeDenmark:T', title='Tidspunkt', format='%Y-%m-%d %H:%M'), alt.Tooltip('DurationMinutes:Q', title='Varighed (minutter)'), alt.Tooltip('AgentDisplayName:N', title='Agent')]
        ).properties(
            height=500
        )
        st.altair_chart(chart, use_container_width=True)
    elif content_tabs == 'Uge':
        st.write("This is the Varighed af samtale(Uge) tab")
    elif content_tabs == 'Måned':
        st.write("Varighed af samtale(Måned)")
    elif content_tabs == 'Kvartal':
        st.write("This is the Varighed af samtale(Kvatal) tab")


show_conversation_duration()
