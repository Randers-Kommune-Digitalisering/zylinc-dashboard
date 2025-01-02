import streamlit as st
import streamlit_antd_components as sac
from datetime import datetime, timedelta
import altair as alt
from utils.time import convert_minutes_to_hms
import pandas as pd


def show_queue_time():
    if 'historical_data' not in st.session_state:
        st.warning("Upload venligst en CSV fil på upload-siden for at fortsætte.")
        st.stop()

    historical_data = st.session_state['historical_data']

    col_1 = st.columns([1])[0]

    with col_1:
        content_tabs = sac.tabs([
            sac.TabsItem('Dag', tag='Dag'),
            sac.TabsItem('Uge', tag='Uge'),
            sac.TabsItem('Måned', tag='Måned'),
        ], color='dark', size='md', position='top', align='start', use_container_width=True)

    if content_tabs == 'Dag':

        unique_dates = historical_data['StartTimeDenmark'].dt.date.unique()
        selected_date = st.date_input("Vælg en dato", min_value=min(unique_dates), max_value=max(unique_dates), key='date_input')

        historical_data_today = historical_data[(historical_data['StartTimeDenmark'].dt.date == selected_date) &
                                                (historical_data['StartTimeDenmark'].dt.time.between(datetime.strptime('06:00', '%H:%M').time(), datetime.strptime('16:00', '%H:%M').time()))]

        avg_wait_time_today = historical_data_today['QueueDurationMinutes'].mean()

        avg_wait_time_today = 0 if pd.isna(avg_wait_time_today) else avg_wait_time_today

        st.metric(label="Gennemsnitlig ventetid(Dag)", value=convert_minutes_to_hms(avg_wait_time_today))

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

    if content_tabs == 'Uge':
        unique_years = historical_data['StartTimeDenmark'].dt.year.unique()
        selected_year = st.selectbox("Vælg et år", unique_years, format_func=lambda x: f'{x}')

        unique_weeks = historical_data[historical_data['StartTimeDenmark'].dt.year == selected_year]['StartTimeDenmark'].dt.isocalendar().week.unique()
        selected_week = st.selectbox("Vælg en uge", unique_weeks, format_func=lambda x: f'Uge {x}')

        start_of_week = pd.to_datetime(f'{selected_year}-W{int(selected_week)}-1', format='%Y-W%W-%w')
        end_of_week = start_of_week + timedelta(days=6)

        historical_data_week = historical_data[(historical_data['StartTimeDenmark'] >= start_of_week) &
                                               (historical_data['StartTimeDenmark'] <= end_of_week)]

        avg_wait_time_week = historical_data_week['QueueDurationMinutes'].mean()
        avg_wait_time_week = 0 if pd.isna(avg_wait_time_week) else avg_wait_time_week

        st.metric(label="Gennemsnitlig ventetid(Uge)", value=convert_minutes_to_hms(avg_wait_time_week))

        queue_data = historical_data_week[historical_data_week['ConversationEventType'].isin(['JoinedQueue', 'LeftQueue'])]

        queue_data['QueueDurationHMS'] = queue_data['QueueDurationMinutes'].apply(convert_minutes_to_hms)

        st.write("## Ventetid i kø (Uge)")
        chart = alt.Chart(queue_data).mark_bar().encode(
            x=alt.X('StartTimeDenmark:T', title='Tidspunkt', axis=alt.Axis(format='%Y-%m-%d %H:%M')),
            y=alt.Y('QueueDurationMinutes:Q', title='Ventetid (minutter)'),
            color=alt.Color('QueueName:N', title='Kø'),
            tooltip=[alt.Tooltip('StartTimeDenmark:T', title='Tidspunkt', format='%Y-%m-%d %H:%M'), alt.Tooltip('QueueDurationHMS:N', title='Ventetid'), alt.Tooltip('QueueName:N', title='Kø')]
        ).properties(
            height=500
        )
        st.altair_chart(chart, use_container_width=True)

    if content_tabs == 'Måned':
        unique_years = historical_data['StartTimeDenmark'].dt.year.unique()
        selected_year = st.selectbox("Vælg et år", unique_years, format_func=lambda x: f'{x}', key='year_select')

        unique_months = historical_data[historical_data['StartTimeDenmark'].dt.year == selected_year]['StartTimeDenmark'].dt.to_period('M').unique()
        month_names = {1: 'Januar', 2: 'Februar', 3: 'Marts', 4: 'April', 5: 'Maj', 6: 'Juni', 7: 'Juli', 8: 'August', 9: 'September', 10: 'Oktober', 11: 'November', 12: 'December'}
        month_options = [(month.month, month_names[month.month]) for month in unique_months]
        selected_month = st.selectbox("Vælg en måned", month_options, format_func=lambda x: x[1], key='month_select')

        selected_month_number = selected_month[0]

        historical_data_month = historical_data[historical_data['StartTimeDenmark'].dt.to_period('M') == pd.Period(year=selected_year, month=selected_month_number, freq='M')]

        avg_wait_time_month = historical_data_month['QueueDurationMinutes'].mean()
        avg_wait_time_month = 0 if pd.isna(avg_wait_time_month) else avg_wait_time_month

        st.metric(label="Gennemsnitlig ventetid(Måned)", value=convert_minutes_to_hms(avg_wait_time_month))

        queue_data = historical_data_month[historical_data_month['ConversationEventType'].isin(['JoinedQueue', 'LeftQueue'])]

        queue_data['QueueDurationHMS'] = queue_data['QueueDurationMinutes'].apply(convert_minutes_to_hms)

        st.write("## Ventetid i kø (Måned)")
        chart = alt.Chart(queue_data).mark_bar().encode(
            x=alt.X('StartTimeDenmark:T', title='Tidspunkt', axis=alt.Axis(format='%Y-%m-%d %H:%M')),
            y=alt.Y('QueueDurationMinutes:Q', title='Ventetid (minutter)'),
            color=alt.Color('QueueName:N', title='Kø'),
            tooltip=[alt.Tooltip('StartTimeDenmark:T', title='Tidspunkt', format='%Y-%m-%d %H:%M'), alt.Tooltip('QueueDurationHMS:N', title='Ventetid'), alt.Tooltip('QueueName:N', title='Kø')]
        ).properties(
            height=500
        )
        st.altair_chart(chart, use_container_width=True)
