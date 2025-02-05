import streamlit as st
import streamlit_antd_components as sac
from datetime import datetime, timedelta
import altair as alt
from utils.time import convert_minutes_to_hms
import pandas as pd


def show_queue_time():
    if 'historical_data' not in st.session_state:
        st.warning("Gå venligst ind på Hent historisk data siden for at hente data")
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

        historical_data_today = historical_data[
            (historical_data['StartTimeDenmark'].dt.date == selected_date) &
            (historical_data['StartTimeDenmark'].dt.time.between(
                datetime.strptime('06:00', '%H:%M').time(),
                datetime.strptime('16:00', '%H:%M').time()
            ))
        ]

        avg_wait_time_today = historical_data_today['QueueDurationMinutes'].mean()

        avg_wait_time_today = 0 if pd.isna(avg_wait_time_today) else avg_wait_time_today

        st.metric(label="Gennemsnitlig ventetid(Dag)", value=convert_minutes_to_hms(avg_wait_time_today))

        queue_data = historical_data_today[historical_data_today['ConversationEventType'].isin(['JoinedQueue', 'LeftQueue'])]

        queue_data['QueueDurationHMS'] = queue_data['QueueDurationMinutes'].apply(convert_minutes_to_hms)
        queue_data['TimeInterval'] = queue_data['StartTimeDenmark'].dt.floor('30T')
        interval_data = queue_data.groupby(['TimeInterval', 'QueueName']).agg({'QueueDurationMinutes': 'mean'}).reset_index()

        st.write(f"## Ventetid i kø (Dag) - {selected_date}")
        chart = alt.Chart(interval_data).mark_bar().encode(
            x=alt.X('TimeInterval:T', title='Tidspunkt', axis=alt.Axis(format='%H:%M')),
            y=alt.Y('QueueDurationMinutes:Q', title='Ventetid (minutter)'),
            color=alt.Color('QueueName:N', title='Kø'),
            tooltip=[alt.Tooltip('TimeInterval:T', title='Tidspunkt', format='%H:%M'), alt.Tooltip('QueueDurationMinutes:Q', title='Ventetid (minutter)'), alt.Tooltip('QueueName:N', title='Kø')]
        ).properties(
            height=700,
            width=900
        )
        st.altair_chart(chart, use_container_width=True)

    if content_tabs == 'Uge':
        unique_years = historical_data['StartTimeDenmark'].dt.year.unique()
        selected_year_week = st.selectbox(
            "Vælg et år",
            unique_years,
            format_func=lambda x: f'{x}',
            index=unique_years.tolist().index(st.session_state['selected_year_week']) if 'selected_year_week' in st.session_state and st.session_state['selected_year_week'] is not None else 0,
            key='year_select_week'
        )

        unique_weeks = historical_data[historical_data['StartTimeDenmark'].dt.year == selected_year_week]['StartTimeDenmark'].dt.isocalendar().week.unique()

        if 'selected_week' not in st.session_state or st.session_state['selected_week'] not in unique_weeks:
            st.session_state['selected_week'] = unique_weeks[0] if unique_weeks else None

        selected_week = st.selectbox(
            "Vælg en uge",
            unique_weeks,
            format_func=lambda x: f'Uge {x}',
            index=unique_weeks.tolist().index(st.session_state['selected_week']) if 'selected_week' in st.session_state and st.session_state['selected_week'] is not None else 0,
            key='week_select'
        )

        st.session_state['selected_year_week'] = selected_year_week
        st.session_state['selected_week'] = selected_week

        start_of_week = pd.to_datetime(f'{selected_year_week}-W{int(selected_week)}-1', format='%Y-W%W-%w')
        end_of_week = start_of_week + timedelta(days=6)

        historical_data_week = historical_data[
            (historical_data['StartTimeDenmark'] >= start_of_week) &
            (historical_data['StartTimeDenmark'] <= end_of_week)
        ]

        historical_data_week = historical_data_week[historical_data_week['StartTimeDenmark'].dt.weekday < 5]

        avg_wait_time_week = historical_data_week['QueueDurationMinutes'].mean()
        avg_wait_time_week = 0 if pd.isna(avg_wait_time_week) else avg_wait_time_week

        st.metric(label="Gennemsnitlig ventetid(Uge)", value=convert_minutes_to_hms(avg_wait_time_week))

        queue_data = historical_data_week[historical_data_week['ConversationEventType'].isin(['JoinedQueue', 'LeftQueue'])]

        queue_data['QueueDurationHMS'] = queue_data['QueueDurationMinutes'].apply(convert_minutes_to_hms)

        weekdays = {0: 'Mandag', 1: 'Tirsdag', 2: 'Onsdag', 3: 'Torsdag', 4: 'Fredag'}
        queue_data['Day'] = queue_data['StartTimeDenmark'].dt.weekday.map(weekdays)
        daily_queue_data = queue_data.groupby('Day').agg({'QueueDurationMinutes': 'sum', 'QueueName': 'first'}).reset_index()

        st.write(f"## Ventetid i kø (Uge) - {selected_year_week}, Uge {selected_week}")
        chart = alt.Chart(daily_queue_data).mark_bar().encode(
            x=alt.X('Day:N', title='Dag', sort=['Mandag', 'Tirsdag', 'Onsdag', 'Torsdag', 'Fredag']),
            y=alt.Y('QueueDurationMinutes:Q', title='Ventetid (minutter)'),
            color=alt.Color('QueueName:N', title='Kø'),
            tooltip=[alt.Tooltip('Day:N', title='Dag'), alt.Tooltip('QueueDurationMinutes:Q', title='Ventetid (minutter)'), alt.Tooltip('QueueName:N', title='Kø')]
        ).properties(
            height=700,
            width=900
        )
        st.altair_chart(chart, use_container_width=True)

    if content_tabs == 'Måned':
        unique_years = historical_data['StartTimeDenmark'].dt.year.unique()
        selected_year_month = st.selectbox(
            "Vælg et år",
            unique_years,
            format_func=lambda x: f'{x}',
            index=unique_years.tolist().index(st.session_state['selected_year_month']) if 'selected_year_month' in st.session_state and st.session_state['selected_year_month'] is not None else 0,
            key='year_select_month'
        )

        unique_months = historical_data[historical_data['StartTimeDenmark'].dt.year == selected_year_month]['StartTimeDenmark'].dt.to_period('M').unique()
        month_names = {1: 'Januar', 2: 'Februar', 3: 'Marts', 4: 'April', 5: 'Maj', 6: 'Juni', 7: 'Juli', 8: 'August', 9: 'September', 10: 'Oktober', 11: 'November', 12: 'December'}
        month_options = [(month.month, month_names[month.month]) for month in unique_months]

        if 'selected_month' not in st.session_state or st.session_state['selected_month'] is None:
            st.session_state['selected_month'] = month_options[0][0] if month_options else None

        selected_month = st.selectbox(
            "Vælg en måned",
            month_options,
            format_func=lambda x: x[1],
            index=[month[0] for month in month_options].index(st.session_state['selected_month']) if 'selected_month' in st.session_state and st.session_state['selected_month'] is not None else 0,
            key='month_select'
        )

        st.session_state['selected_year_month'] = selected_year_month
        st.session_state['selected_month'] = selected_month[0]

        selected_month_number = selected_month[0]

        historical_data_month = historical_data[historical_data['StartTimeDenmark'].dt.to_period('M') == pd.Period(year=selected_year_month, month=selected_month_number, freq='M')]

        avg_wait_time_month = historical_data_month['QueueDurationMinutes'].mean()
        avg_wait_time_month = 0 if pd.isna(avg_wait_time_month) else avg_wait_time_month

        st.metric(label="Gennemsnitlig ventetid(Måned)", value=convert_minutes_to_hms(avg_wait_time_month))

        queue_data = historical_data_month[historical_data_month['ConversationEventType'].isin(['JoinedQueue', 'LeftQueue'])]

        queue_data['QueueDurationHMS'] = queue_data['QueueDurationMinutes'].apply(convert_minutes_to_hms)

        queue_data['Day'] = queue_data['StartTimeDenmark'].dt.day
        daily_queue_data = queue_data.groupby('Day').agg({'QueueDurationMinutes': 'sum', 'QueueName': 'first'}).reset_index()

        st.write(f"## Ventetid i kø (Måned) - {selected_year_month}, Måned {month_names[selected_month_number]}")
        chart = alt.Chart(daily_queue_data).mark_bar().encode(
            x=alt.X('Day:O', title='Dag', axis=alt.Axis(format='d')),
            y=alt.Y('QueueDurationMinutes:Q', title='Ventetid (minutter)'),
            color=alt.Color('QueueName:N', title='Kø'),
            tooltip=[alt.Tooltip('Day:O', title='Dag'), alt.Tooltip('QueueDurationMinutes:Q', title='Ventetid (minutter)'), alt.Tooltip('QueueName:N', title='Kø')]
        ).properties(
            height=700,
            width=900
        )
        st.altair_chart(chart, use_container_width=True)
