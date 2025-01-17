import streamlit as st
import streamlit_antd_components as sac
from datetime import datetime
import altair as alt
import pandas as pd
from utils.time import convert_minutes_to_hms


def show_conversation_duration():
    if 'historical_data' not in st.session_state:
        st.warning("Gå venligst ind på Hent historisk data siden for at hente data")
        st.stop()

    historical_data = st.session_state['historical_data']

    col_1 = st.columns([1])[0]

    with col_1:
        content_tabs = sac.tabs([
            sac.TabsItem('Dag', tag='Dag'),
            sac.TabsItem('Uge', tag='Uge'),
            sac.TabsItem('Kvartal', tag='Kvartal'),
        ], color='dark', size='md', position='top', align='start', use_container_width=True)

    if content_tabs == 'Dag':
        unique_dates = historical_data['StartTimeDenmark'].dt.date.unique()
        selected_date = st.date_input("Vælg en dato", min_value=min(unique_dates), max_value=max(unique_dates), key='date_input')

        historical_data_today = historical_data[(historical_data['StartTimeDenmark'].dt.date == selected_date) &
                                                (historical_data['StartTimeDenmark'].dt.time.between(datetime.strptime('06:00', '%H:%M').time(), datetime.strptime('16:00', '%H:%M').time()))]

        avg_duration_today = historical_data_today[historical_data_today['Result'] == 'Answered']['DurationMinutes'].mean()

        st.metric(label="Gennemsnitlig varighed af besvarede opkald(Dag)", value=convert_minutes_to_hms(avg_duration_today))

        historical_data_today['TimeInterval'] = historical_data_today['StartTimeDenmark'].dt.floor('30T')
        chart_data = historical_data_today.groupby(['TimeInterval', 'AgentDisplayName']).agg({'DurationMinutes': 'mean'}).reset_index()

        st.write(f"## Varighed af samtale(Dag) - {selected_date}")
        chart = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('TimeInterval:T', title='Tidspunkt', axis=alt.Axis(format='%H:%M')),
            y=alt.Y('DurationMinutes:Q', title='Varighed (minutter)'),
            color=alt.Color('AgentDisplayName:N', title='Medarbejder'),
            tooltip=[alt.Tooltip('TimeInterval:T', title='Tidspunkt', format='%H:%M'), alt.Tooltip('DurationMinutes:Q', title='Varighed (minutter)'), alt.Tooltip('AgentDisplayName:N', title='Medarbejder')]
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
        end_of_week = start_of_week + pd.Timedelta(days=6)

        historical_data_week = historical_data[(historical_data['StartTimeDenmark'] >= start_of_week) &
                                               (historical_data['StartTimeDenmark'] <= end_of_week) &
                                               (historical_data['StartTimeDenmark'].dt.time.between(datetime.strptime('06:00', '%H:%M').time(), datetime.strptime('16:00', '%H:%M').time()))]

        avg_duration_week = historical_data_week[historical_data_week['Result'] == 'Answered']['DurationMinutes'].mean()

        st.metric(label="Gennemsnitlig varighed af besvarede opkald(Uge)", value=convert_minutes_to_hms(avg_duration_week))

        chart_data = historical_data_week[['StartTimeDenmark', 'DurationMinutes', 'AgentDisplayName']]

        st.write(f"## Varighed af samtale(Uge) - {selected_year}, Uge {selected_week}")
        chart = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('StartTimeDenmark:T', title='Tidspunkt', axis=alt.Axis(format='%Y-%m-%d %H:%M')),
            y=alt.Y('DurationMinutes:Q', title='Varighed (minutter)'),
            color=alt.Color('AgentDisplayName:N', title='Medarbejder'),
            tooltip=[alt.Tooltip('StartTimeDenmark:T', title='Tidspunkt', format='%Y-%m-%d %H:%M'), alt.Tooltip('DurationMinutes:Q', title='Varighed (minutter)'), alt.Tooltip('AgentDisplayName:N', title='Medarbejder')]
        ).properties(
            height=500
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

        avg_duration_quarter = historical_data_quarter[historical_data_quarter['Result'] == 'Answered']['DurationMinutes'].mean()

        st.metric(label="Gennemsnitlig varighed af besvarede opkald(Kvartal)", value=convert_minutes_to_hms(avg_duration_quarter))

        chart_data = historical_data_quarter[['StartTimeDenmark', 'DurationMinutes', 'AgentDisplayName']]

        st.write(f"## Varighed af samtale(Kvartal) - {quarter_names[selected_quarter_number]} {selected_year}")
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
