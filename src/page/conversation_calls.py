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

        historical_data_today = historical_data[(historical_data['StartTimeDenmark'].dt.date == selected_date) &
                                                (historical_data['StartTimeDenmark'].dt.time.between(datetime.strptime('06:00', '%H:%M').time(), datetime.strptime('16:00', '%H:%M').time()))]

        answered_calls_today = historical_data_today[historical_data_today['Result'] == 'Answered']

        answered_calls_today_count = answered_calls_today.shape[0]

        previous_date = selected_date - timedelta(days=1)
        historical_data_yesterday = historical_data[(historical_data['StartTimeDenmark'].dt.date == previous_date) &
                                                    (historical_data['StartTimeDenmark'].dt.time.between(datetime.strptime('06:00', '%H:%M').time(), datetime.strptime('16:00', '%H:%M').time()))]

        answered_calls_yesterday_count = historical_data_yesterday[historical_data_yesterday['Result'] == 'Answered'].shape[0]

        delta_answered_calls = answered_calls_today_count - answered_calls_yesterday_count

        st.metric(label="Antal besvarede opkald (Dag)", value=answered_calls_today_count, delta=delta_answered_calls)

        answered_calls_today['Hour'] = answered_calls_today['StartTimeDenmark'].dt.floor('H')
        hourly_data = answered_calls_today.groupby('Hour').size().reset_index(name='Antal samtaler')

        st.write("## Antal samtaler (Dag)")
        base = alt.Chart(hourly_data).encode(
            x=alt.X('Hour:T', title='Tidspunkt', axis=alt.Axis(format='%Y-%m-%d %H:%M')),
            y=alt.Y('Antal samtaler:Q', title='Antal samtaler')
        ).properties(
            height=500
        )

        points = base.mark_circle(size=60).encode(
            tooltip=[alt.Tooltip('Hour:T', title='Tidspunkt', format='%Y-%m-%d %H:%M'), alt.Tooltip('Antal samtaler:Q', title='Antal samtaler')]
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

        previous_week_start = start_of_week - timedelta(weeks=1)
        previous_week_end = end_of_week - timedelta(weeks=1)

        historical_data_previous_week = historical_data[(historical_data['StartTimeDenmark'] >= previous_week_start) &
                                                        (historical_data['StartTimeDenmark'] <= previous_week_end)]

        answered_calls_week = historical_data_week[historical_data_week['Result'] == 'Answered'].shape[0]
        answered_calls_previous_week = historical_data_previous_week[historical_data_previous_week['Result'] == 'Answered'].shape[0]

        delta_answered_calls_week = answered_calls_week - answered_calls_previous_week

        st.metric(label="Antal besvarede opkald (Uge)", value=answered_calls_week, delta=delta_answered_calls_week)

        chart_data = historical_data_week[historical_data_week['Result'] == 'Answered']
        chart_data['DayOfWeek'] = chart_data['StartTimeDenmark'].dt.day_name()

        day_name_map = {
            'Monday': 'Mandag',
            'Tuesday': 'Tirsdag',
            'Wednesday': 'Onsdag',
            'Thursday': 'Torsdag',
            'Friday': 'Fredag'
        }
        chart_data['DayOfWeek'] = chart_data['DayOfWeek'].map(day_name_map)

        chart_data['DateWithWeekday'] = chart_data['StartTimeDenmark'].dt.strftime('%Y-%m-%d') + ' (' + chart_data['DayOfWeek'] + ')'

        all_weekdays = ['Mandag', 'Tirsdag', 'Onsdag', 'Torsdag', 'Fredag']
        all_dates_with_weekdays = [chart_data[chart_data['DayOfWeek'] == day]['DateWithWeekday'].iloc[0] if not chart_data[chart_data['DayOfWeek'] == day].empty else f'No data ({day})' for day in all_weekdays]

        chart_data['DateWithWeekday'] = pd.Categorical(
            chart_data['DateWithWeekday'],
            categories=all_dates_with_weekdays,
            ordered=True
        )

        st.write("## Antal samtaler (Uge)")
        base = alt.Chart(chart_data).encode(
            x=alt.X('DateWithWeekday:N', title='Ugedag', axis=alt.Axis(labelAngle=0)),
            y=alt.Y('count()', title='Antal samtaler')
        ).properties(
            height=500
        )

        points = base.mark_circle(size=60).encode(
            tooltip=[alt.Tooltip('DateWithWeekday:N', title='Ugedag'), alt.Tooltip('count()', title='Antal samtaler')]
        )

        text = base.mark_text(
            align='left',
            baseline='middle',
            dx=7
        ).encode(
            text='count()'
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

        answered_calls_month = historical_data_month[historical_data_month['Result'] == 'Answered']

        answered_calls_month_count = answered_calls_month.shape[0]

        previous_month = pd.Period(year=selected_year, month=selected_month_number, freq='M') - 1
        historical_data_previous_month = historical_data[historical_data['StartTimeDenmark'].dt.to_period('M') == previous_month]

        answered_calls_previous_month_count = historical_data_previous_month[historical_data_previous_month['Result'] == 'Answered'].shape[0]

        delta_answered_calls = answered_calls_month_count - answered_calls_previous_month_count

        st.metric(label="Antal besvarede opkald (Måned)", value=answered_calls_month_count, delta=delta_answered_calls)

        answered_calls_month['Day'] = answered_calls_month['StartTimeDenmark'].dt.floor('D')
        daily_data = answered_calls_month.groupby('Day').size().reset_index(name='Antal samtaler')

        st.write("## Antal samtaler (Måned)")
        base = alt.Chart(daily_data).encode(
            x=alt.X('Day:T', title='Tidspunkt', axis=alt.Axis(format='%Y-%m-%d')),
            y=alt.Y('Antal samtaler:Q', title='Antal samtaler')
        ).properties(
            height=500
        )

        points = base.mark_circle(size=60).encode(
            tooltip=[alt.Tooltip('Day:T', title='Tidspunkt', format='%Y-%m-%d'), alt.Tooltip('Antal samtaler:Q', title='Antal samtaler')]
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
