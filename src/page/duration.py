import streamlit as st
import streamlit_antd_components as sac
from datetime import datetime, timedelta
import altair as alt
import pandas as pd


def show_conversation_duration():
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
            sac.TabsItem('Kvartal', tag='Kvartal'),
        ], color='dark', size='md', position='top', align='start', use_container_width=True)

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
        st.metric(label="Antal mistede opkald", value=missed_calls_today, delta=delta_missed_calls, delta_color="inverse")

        chart_data = historical_data_today[['StartTimeDenmark', 'DurationMinutes', 'AgentDisplayName']]

        st.write("## Varighed af samtale(Dag)")
        chart = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('StartTimeDenmark:T', title='Tidspunkt', axis=alt.Axis(format='%Y-%m-%d %H:%M')),
            y=alt.Y('DurationMinutes:Q', title='Varighed (minutter)'),
            color=alt.Color('AgentDisplayName:N', title='Medarbejder'),
            tooltip=[alt.Tooltip('StartTimeDenmark:T', title='Tidspunkt', format='%Y-%m-%d %H:%M'), alt.Tooltip('DurationMinutes:Q', title='Varighed (minutter)'), alt.Tooltip('AgentDisplayName:N', title='Medarbejder')]
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

        previous_week_start = start_of_week - timedelta(weeks=1)
        previous_week_end = end_of_week - timedelta(weeks=1)

        historical_data_previous_week = historical_data[(historical_data['StartTimeDenmark'] >= previous_week_start) &
                                                        (historical_data['StartTimeDenmark'] <= previous_week_end)]

        answered_calls_week = historical_data_week[historical_data_week['Result'] == 'Answered'].shape[0]
        missed_calls_week = historical_data_week[historical_data_week['Result'] == 'Missed'].shape[0]

        answered_calls_previous_week = historical_data_previous_week[historical_data_previous_week['Result'] == 'Answered'].shape[0]
        missed_calls_previous_week = historical_data_previous_week[historical_data_previous_week['Result'] == 'Missed'].shape[0]

        delta_answered_calls_week = answered_calls_week - answered_calls_previous_week
        delta_missed_calls_week = missed_calls_week - missed_calls_previous_week

        st.metric(label="Antal besvarede opkald (Uge)", value=answered_calls_week, delta=delta_answered_calls_week)
        st.metric(label="Antal mistede opkald (Uge)", value=missed_calls_week, delta=delta_missed_calls_week, delta_color="inverse")

        chart_data = historical_data_week[['StartTimeDenmark', 'DurationMinutes', 'AgentDisplayName']]
        chart_data['DayOfWeek'] = chart_data['StartTimeDenmark'].dt.day_name()

        day_name_map = {
            'Monday': 'Mandag',
            'Tuesday': 'Tirsdag',
            'Wednesday': 'Onsdag',
            'Thursday': 'Torsdag',
            'Friday': 'Fredag'
        }
        chart_data['DayOfWeek'] = chart_data['DayOfWeek'].map(day_name_map)

        st.write("## Varighed af samtale(Uge)")
        chart = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('DayOfWeek:N', title='Ugedag', sort=['Mandag', 'Tirsdag', 'Onsdag', 'Torsdag', 'Fredag'], axis=alt.Axis(labelAngle=0)),
            y=alt.Y('DurationMinutes:Q', title='Varighed (minutter)'),
            color=alt.Color('AgentDisplayName:N', title='Medarbejder'),
            tooltip=[alt.Tooltip('StartTimeDenmark:T', title='Tidspunkt', format='%Y-%m-%d %H:%M'), alt.Tooltip('DurationMinutes:Q', title='Varighed (minutter)'), alt.Tooltip('AgentDisplayName:N', title='Medarbejder')]
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

        previous_month = pd.Period(year=selected_year, month=selected_month_number, freq='M') - 1
        historical_data_previous_month = historical_data[historical_data['StartTimeDenmark'].dt.to_period('M') == previous_month]

        answered_calls_month = historical_data_month[historical_data_month['Result'] == 'Answered'].shape[0]
        missed_calls_month = historical_data_month[historical_data_month['Result'] == 'Missed'].shape[0]

        answered_calls_previous_month = historical_data_previous_month[historical_data_previous_month['Result'] == 'Answered'].shape[0]
        missed_calls_previous_month = historical_data_previous_month[historical_data_previous_month['Result'] == 'Missed'].shape[0]

        delta_answered_calls = answered_calls_month - answered_calls_previous_month
        delta_missed_calls = missed_calls_month - missed_calls_previous_month

        st.metric(label="Antal besvarede opkald", value=answered_calls_month, delta=delta_answered_calls)
        st.metric(label="Antal mistede opkald", value=missed_calls_month, delta=delta_missed_calls, delta_color="inverse")

        chart_data = historical_data_month[['StartTimeDenmark', 'DurationMinutes', 'AgentDisplayName']]

        st.write("## Varighed af samtale(Måned)")
        chart = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('StartTimeDenmark:T', title='Tidspunkt', axis=alt.Axis(format='%Y-%m-%d %H:%M')),
            y=alt.Y('DurationMinutes:Q', title='Varighed (minutter)'),
            color=alt.Color('AgentDisplayName:N', title='Medarbejder'),
            tooltip=[alt.Tooltip('StartTimeDenmark:T', title='Tidspunkt', format='%Y-%m-%d %H:%M'), alt.Tooltip('DurationMinutes:Q', title='Varighed (minutter)'), alt.Tooltip('AgentDisplayName:N', title='Medarbejder')]
        ).properties(
            height=500
        ).facet(
            facet=alt.Facet('AgentDisplayName:N', title='Medarbejder'),
            columns=1
        )
        st.altair_chart(chart, use_container_width=True)
    if content_tabs == 'Kvartal':
        unique_years = historical_data['StartTimeDenmark'].dt.year.unique()
        selected_year = st.selectbox("Vælg et år", unique_years, format_func=lambda x: f'År {x}', key='year_select')

        unique_quarters = historical_data[historical_data['StartTimeDenmark'].dt.year == selected_year]['StartTimeDenmark'].dt.to_period('Q').unique()
        quarter_names = {1: 'Q1', 2: 'Q2', 3: 'Q3', 4: 'Q4'}
        quarter_options = [(quarter.quarter, quarter_names[quarter.quarter]) for quarter in unique_quarters]
        selected_quarter = st.selectbox("Vælg et kvartal", quarter_options, format_func=lambda x: x[1], key='quarter_select')

        selected_quarter_number = selected_quarter[0]

        historical_data_quarter = historical_data[historical_data['StartTimeDenmark'].dt.to_period('Q') == pd.Period(year=selected_year, quarter=selected_quarter_number, freq='Q')]

        previous_quarter = pd.Period(year=selected_year, quarter=selected_quarter_number, freq='Q') - 1
        historical_data_previous_quarter = historical_data[historical_data['StartTimeDenmark'].dt.to_period('Q') == previous_quarter]

        answered_calls_quarter = historical_data_quarter[historical_data_quarter['Result'] == 'Answered'].shape[0]
        missed_calls_quarter = historical_data_quarter[historical_data_quarter['Result'] == 'Missed'].shape[0]

        answered_calls_previous_quarter = historical_data_previous_quarter[historical_data_previous_quarter['Result'] == 'Answered'].shape[0]
        missed_calls_previous_quarter = historical_data_previous_quarter[historical_data_previous_quarter['Result'] == 'Missed'].shape[0]

        delta_answered_calls = answered_calls_quarter - answered_calls_previous_quarter
        delta_missed_calls = missed_calls_quarter - missed_calls_previous_quarter

        st.metric(label="Antal besvarede opkald", value=answered_calls_quarter, delta=delta_answered_calls)
        st.metric(label="Antal mistede opkald", value=missed_calls_quarter, delta=delta_missed_calls, delta_color="inverse")

        chart_data = historical_data_quarter[['StartTimeDenmark', 'DurationMinutes', 'AgentDisplayName']]

        st.write("## Varighed af samtale(Kvartal)")
        chart = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('StartTimeDenmark:T', title='Tidspunkt', axis=alt.Axis(format='%Y-%m-%d %H:%M')),
            y=alt.Y('DurationMinutes:Q', title='Varighed (minutter)'),
            color=alt.Color('AgentDisplayName:N', title='Medarbejder'),
            tooltip=[alt.Tooltip('StartTimeDenmark:T', title='Tidspunkt', format='%Y-%m-%d %H:%M'), alt.Tooltip('DurationMinutes:Q', title='Varighed (minutter)'), alt.Tooltip('AgentDisplayName:N', title='Medarbejder')]
        ).properties(
            height=500
        ).facet(
            facet=alt.Facet('AgentDisplayName:N', title='Medarbejder'),
            columns=1
        )
        st.altair_chart(chart, use_container_width=True)
