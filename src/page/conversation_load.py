import streamlit as st
import streamlit_antd_components as sac
import altair as alt
from datetime import datetime, timedelta
import pandas as pd


def show_conversation_load():
    if 'historical_data' not in st.session_state:
        st.warning("Gå venligst ind på Hent historisk data siden for at hente data")
        st.stop()

    historical_data = st.session_state['historical_data']
    historical_data = historical_data[historical_data['Result'].isin(['Answered', 'Missed'])]

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

        historical_data_today = historical_data[historical_data['StartTimeDenmark'].dt.date == selected_date]

        hourly_data = historical_data_today.groupby(historical_data_today['StartTimeDenmark'].dt.hour).size().reset_index(name='Antal samtaler')
        hourly_data.columns = ['Hour', 'Antal samtaler']
        hourly_data['Hour'] = hourly_data['Hour'].apply(lambda x: f'{x:02}:00')

        st.write("## Hvornår på dagen kommer samtalerne")
        base = alt.Chart(hourly_data).encode(
            x=alt.X('Hour:O', title='Time på dagen'),
            y=alt.Y('Antal samtaler:Q', title='Antal samtaler')
        ).properties(
            height=500
        )

        points = base.mark_circle(size=60).encode(
            tooltip=[alt.Tooltip('Hour:O', title='Time på dagen'), alt.Tooltip('Antal samtaler:Q', title='Antal samtaler')]
        )

        text = base.mark_text(
            align='left',
            baseline='middle',
            dx=7
        ).encode(
            text='Antal samtaler:Q'
        )

        chart = points + text

        st.altair_chart(chart.interactive(), use_container_width=True)

    if content_tabs == 'Uge':
        unique_years = historical_data['StartTimeDenmark'].dt.year.unique()
        selected_year = st.selectbox("Vælg et år", unique_years, format_func=lambda x: f'{x}')

        unique_weeks = historical_data[historical_data['StartTimeDenmark'].dt.year == selected_year]['StartTimeDenmark'].dt.isocalendar().week.unique()
        selected_week = st.selectbox("Vælg en uge", unique_weeks, format_func=lambda x: f'Uge {x}')

        start_of_week = pd.to_datetime(f'{selected_year}-W{int(selected_week)}-1', format='%Y-W%W-%w')
        end_of_week = start_of_week + timedelta(days=6)

        historical_data_week = historical_data[(historical_data['StartTimeDenmark'] >= start_of_week) &
                                               (historical_data['StartTimeDenmark'] <= end_of_week)]

        daily_data = historical_data_week.groupby(historical_data_week['StartTimeDenmark'].dt.day_name()).size().reset_index(name='Antal samtaler')
        daily_data.columns = ['DayOfWeek', 'Antal samtaler']

        day_name_map = {
            'Monday': 'Mandag',
            'Tuesday': 'Tirsdag',
            'Wednesday': 'Onsdag',
            'Thursday': 'Torsdag',
            'Friday': 'Fredag',
            'Saturday': 'Lørdag',
            'Sunday': 'Søndag'
        }
        daily_data['DayOfWeek'] = daily_data['DayOfWeek'].map(day_name_map)

        st.write("## Hvornår på ugen kommer samtalerne")
        base = alt.Chart(daily_data).encode(
            x=alt.X('DayOfWeek:N', title='Ugedag', sort=list(day_name_map.values())),
            y=alt.Y('Antal samtaler:Q', title='Antal samtaler')
        ).properties(
            height=500
        )

        points = base.mark_circle(size=60).encode(
            tooltip=[alt.Tooltip('DayOfWeek:N', title='Ugedag'), alt.Tooltip('Antal samtaler:Q', title='Antal samtaler')]
        )

        text = base.mark_text(
            align='left',
            baseline='middle',
            dx=7
        ).encode(
            text='Antal samtaler:Q'
        )

        chart = points + text

        st.altair_chart(chart.interactive(), use_container_width=True)

    if content_tabs == 'Måned':
        unique_years = historical_data['StartTimeDenmark'].dt.year.unique()
        selected_year = st.selectbox("Vælg et år", unique_years, format_func=lambda x: f'{x}', key='year_select')

        unique_months = historical_data[historical_data['StartTimeDenmark'].dt.year == selected_year]['StartTimeDenmark'].dt.to_period('M').unique()
        month_names = {1: 'Januar', 2: 'Februar', 3: 'Marts', 4: 'April', 5: 'Maj', 6: 'Juni', 7: 'Juli', 8: 'August', 9: 'September', 10: 'Oktober', 11: 'November', 12: 'December'}
        month_options = [(month.month, month_names[month.month]) for month in unique_months]
        selected_month = st.selectbox("Vælg en måned", month_options, format_func=lambda x: x[1], key='month_select')

        selected_month_number = selected_month[0]

        historical_data_month = historical_data[historical_data['StartTimeDenmark'].dt.to_period('M') == pd.Period(year=selected_year, month=selected_month_number, freq='M')]

        weekly_data = historical_data_month.groupby(historical_data_month['StartTimeDenmark'].dt.isocalendar().week).size().reset_index(name='Antal samtaler')
        weekly_data.columns = ['Week', 'Antal samtaler']

        st.write("## Hvornår på måneden kommer samtalerne")
        base = alt.Chart(weekly_data).encode(
            x=alt.X('Week:O', title='Uge i måneden'),
            y=alt.Y('Antal samtaler:Q', title='Antal samtaler')
        ).properties(
            height=500
        )

        points = base.mark_circle(size=60).encode(
            tooltip=[alt.Tooltip('Week:O', title='Uge i måneden'), alt.Tooltip('Antal samtaler:Q', title='Antal samtaler')]
        )

        text = base.mark_text(
            align='left',
            baseline='middle',
            dx=7
        ).encode(
            text='Antal samtaler:Q'
        )

        chart = points + text

        st.altair_chart(chart.interactive(), use_container_width=True)