import streamlit as st
import streamlit_antd_components as sac
import altair as alt
from datetime import datetime, timedelta
import pandas as pd


def show_conversation_call():
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
            (historical_data['StartTimeDenmark'].dt.time.between(datetime.strptime('06:00', '%H:%M').time(), datetime.strptime('16:00', '%H:%M').time()))
        ]

        answered_calls_today = historical_data_today[historical_data_today['Result'] == 'Answered']
        answered_calls_today_count = answered_calls_today.shape[0]

        st.metric(label="Antal besvarede opkald (Dag)", value=answered_calls_today_count)

        answered_calls_today['TimeInterval'] = answered_calls_today['StartTimeDenmark'].dt.floor('30T')
        interval_data = answered_calls_today.groupby('TimeInterval').size().reset_index(name='Antal samtaler')

        st.write(f"## Antal samtaler (Dag) - {selected_date}")
        chart = alt.Chart(interval_data).mark_bar().encode(
            x=alt.X('TimeInterval:T', title='Tidspunkt', axis=alt.Axis(format='%H:%M')),
            y=alt.Y('Antal samtaler:Q', title='Antal samtaler'),
            tooltip=[alt.Tooltip('TimeInterval:T', title='Tidspunkt', format='%H:%M'), alt.Tooltip('Antal samtaler:Q', title='Antal samtaler')]
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

        answered_calls_week = historical_data_week[historical_data_week['Result'] == 'Answered'].shape[0]

        st.metric(label="Antal besvarede opkald", value=answered_calls_week)

        historical_data_week['Day'] = historical_data_week['StartTimeDenmark'].dt.floor('D')
        daily_data = historical_data_week[historical_data_week['Result'] == 'Answered'].groupby(['Day', 'Result']).size().reset_index(name='Antal opkald')

        daily_data['DayOfWeek'] = daily_data['Day'].dt.day_name()

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

        all_weekdays = ['Mandag', 'Tirsdag', 'Onsdag', 'Torsdag', 'Fredag']
        daily_data['DayOfWeek'] = pd.Categorical(
            daily_data['DayOfWeek'],
            categories=all_weekdays,
            ordered=True
        )

        st.write(f"## Antal samtaler (Uge) - {selected_year_week}, Uge {selected_week}")

        chart = alt.Chart(daily_data).mark_bar().encode(
            x=alt.X('DayOfWeek:O', title='Ugedag', sort=all_weekdays),
            y='Antal opkald:Q',
            color='Result:N',
            tooltip=[alt.Tooltip('DayOfWeek:O', title='Ugedag'), alt.Tooltip('Antal opkald:Q', title='Antal opkald'), alt.Tooltip('Result:N', title='Resultat')]
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

        answered_calls_month = historical_data_month[historical_data_month['Result'] == 'Answered']

        answered_calls_month_count = answered_calls_month.shape[0]

        st.metric(label="Antal besvarede opkald (Måned)", value=answered_calls_month_count)

        answered_calls_month['Day'] = answered_calls_month['StartTimeDenmark'].dt.floor('D')
        daily_data = answered_calls_month.groupby(['Day', 'Result']).size().reset_index(name='Antal opkald')
        daily_data['Day'] = daily_data['Day'].dt.day

        st.write(f"## Antal samtaler (Måned) - {selected_year_month}, Måned {month_names[selected_month_number]}")

        chart = alt.Chart(daily_data).mark_bar().encode(
            x=alt.X('Day:O', title='Månedsdag'),
            y='Antal opkald:Q',
            color=alt.Color('Result:N', title='Resultat', scale=alt.Scale(domain=['Answered'])),
            tooltip=[alt.Tooltip('Day:O', title='Månedsdag'), alt.Tooltip('Antal opkald:Q', title='Antal besvarede opkald')]
        ).properties(
            height=700,
            width=900
        )

        st.altair_chart(chart, use_container_width=True)
