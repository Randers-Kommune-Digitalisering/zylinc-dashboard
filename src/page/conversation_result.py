import streamlit as st
import streamlit_antd_components as sac
import altair as alt
from datetime import datetime
import pandas as pd


def show_conversation_result():
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

        answered_calls_today = historical_data_today[historical_data_today['Result'] == 'Answered'].shape[0]
        missed_calls_today = historical_data_today[historical_data_today['Result'] == 'Missed'].shape[0]

        st.metric(label="Antal besvarede opkald", value=answered_calls_today)
        st.metric(label="Antal mistede opkald", value=missed_calls_today)

        historical_data_today['TimeInterval'] = historical_data_today['StartTimeDenmark'].dt.floor('30T')
        interval_data = historical_data_today.groupby(['TimeInterval', 'Result']).size().reset_index(name='Antal opkald')

        st.write(f"## Resultat af opkald (Dag) - {selected_date}")
        base = alt.Chart(interval_data).encode(
            x=alt.X('TimeInterval:T', title='Tidspunkt', axis=alt.Axis(format='%H:%M')),
            y=alt.Y('Antal opkald:Q', title='Antal opkald'),
            color=alt.condition(
                alt.datum.Result == 'Answered',
                alt.value('green'),
                alt.value('red')
            )
        ).properties(
            height=500
        )

        points = base.mark_circle(size=60).encode(
            tooltip=[alt.Tooltip('TimeInterval:T', title='Tidspunkt', format='%H:%M'), alt.Tooltip('Antal opkald:Q', title='Antal opkald'), alt.Tooltip('Result:N', title='Resultat')]
        )

        text = base.mark_text(
            align='left',
            baseline='middle',
            dx=7
        ).encode(
            text='Antal opkald:Q'
        )

        chart = points + text

        st.altair_chart(chart.interactive(), use_container_width=True)

    if content_tabs == 'Uge':
        unique_years = historical_data['StartTimeDenmark'].dt.year.unique()
        selected_year = st.selectbox("Vælg et år", unique_years, format_func=lambda x: f'{x}')

        unique_weeks = historical_data[historical_data['StartTimeDenmark'].dt.year == selected_year]['StartTimeDenmark'].dt.isocalendar().week.unique()
        selected_week = st.selectbox("Vælg en uge", unique_weeks, format_func=lambda x: f'Uge {x}')

        start_of_week = pd.to_datetime(f'{selected_year}-W{int(selected_week)}-1', format='%Y-W%W-%w')
        end_of_week = start_of_week + pd.Timedelta(days=6)

        historical_data_week = historical_data[(historical_data['StartTimeDenmark'] >= start_of_week) & (historical_data['StartTimeDenmark'] <= end_of_week)]

        answered_calls_week = historical_data_week[historical_data_week['Result'] == 'Answered'].shape[0]
        missed_calls_week = historical_data_week[historical_data_week['Result'] == 'Missed'].shape[0]

        st.metric(label="Antal besvarede opkald", value=answered_calls_week)
        st.metric(label="Antal mistede opkald", value=missed_calls_week)

        historical_data_week['Day'] = historical_data_week['StartTimeDenmark'].dt.floor('D')
        daily_data = historical_data_week.groupby(['Day', 'Result']).size().reset_index(name='Antal opkald')

        daily_data['DayOfWeek'] = daily_data['Day'].dt.day_name()

        day_name_map = {
            'Monday': 'Mandag',
            'Tuesday': 'Tirsdag',
            'Wednesday': 'Onsdag',
            'Thursday': 'Torsdag',
            'Friday': 'Fredag'
        }
        daily_data['DayOfWeek'] = daily_data['DayOfWeek'].map(day_name_map)

        daily_data['DateWithWeekday'] = daily_data['Day'].dt.strftime('%Y-%m-%d') + ' (' + daily_data['DayOfWeek'] + ')'

        all_weekdays = ['Mandag', 'Tirsdag', 'Onsdag', 'Torsdag', 'Fredag']
        all_dates_with_weekdays = [daily_data[daily_data['DayOfWeek'] == day]['DateWithWeekday'].iloc[0] if not daily_data[daily_data['DayOfWeek'] == day].empty else f'No data ({day})' for day in all_weekdays]

        daily_data['DateWithWeekday'] = pd.Categorical(
            daily_data['DateWithWeekday'],
            categories=all_dates_with_weekdays,
            ordered=True
        )

        st.write(f"## Resultat af opkald (Uge) - {selected_year}, Uge {selected_week}")
        base = alt.Chart(daily_data).encode(
            x=alt.X('DateWithWeekday:N', title='Ugedag', axis=alt.Axis(labelAngle=0)),
            y=alt.Y('Antal opkald:Q', title='Antal opkald'),
            color=alt.condition(
                alt.datum.Result == 'Answered',
                alt.value('green'),
                alt.value('red')
            )
        ).properties(
            height=500
        )

        points = base.mark_circle(size=60).encode(
            tooltip=[alt.Tooltip('DateWithWeekday:N', title='Ugedag'), alt.Tooltip('Antal opkald:Q', title='Antal opkald'), alt.Tooltip('Result:N', title='Resultat')]
        )

        text = base.mark_text(
            align='left',
            baseline='middle',
            dx=7
        ).encode(
            text='Antal opkald:Q'
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

        answered_calls_month = historical_data_month[historical_data_month['Result'] == 'Answered'].shape[0]
        missed_calls_month = historical_data_month[historical_data_month['Result'] == 'Missed'].shape[0]

        st.metric(label="Antal besvarede opkald", value=answered_calls_month)
        st.metric(label="Antal mistede opkald", value=missed_calls_month)

        historical_data_month['Day'] = historical_data_month['StartTimeDenmark'].dt.floor('D')
        daily_data = historical_data_month.groupby(['Day', 'Result']).size().reset_index(name='Antal opkald')

        st.write(f"## Resultat af opkald (Måned) - {selected_year}, Måned {month_names[selected_month_number]}")
        base = alt.Chart(daily_data).encode(
            x=alt.X('Day:T', title='Tidspunkt', axis=alt.Axis(format='%Y-%m-%d')),
            y=alt.Y('Antal opkald:Q', title='Antal opkald'),
            color=alt.condition(
                alt.datum.Result == 'Answered',
                alt.value('green'),
                alt.value('red')
            )
        ).properties(
            height=500
        )

        points = base.mark_circle(size=60).encode(
            tooltip=[alt.Tooltip('Day:T', title='Tidspunkt', format='%Y-%m-%d'), alt.Tooltip('Antal opkald:Q', title='Antal opkald'), alt.Tooltip('Result:N', title='Resultat')]
        )

        text = base.mark_text(
            align='left',
            baseline='middle',
            dx=7
        ).encode(
            text='Antal opkald:Q'
        )

        chart = points + text

        st.altair_chart(chart.interactive(), use_container_width=True)
