import pandas as pd
import pytz
from datetime import datetime


def convert_milliseconds_to_minutes(ms):
    return ms / (1000 * 60)


def convert_to_denmark_time(utc_time):
    utc = pytz.utc
    cet = pytz.timezone('Europe/Copenhagen')
    utc_dt = utc.localize(datetime.strptime(utc_time, '%Y-%m-%d %H:%M:%S'))
    cet_dt = utc_dt.astimezone(cet)
    return cet_dt.strftime('%Y-%m-%d %H:%M:%S')


def load_and_process_data(file_path):
    historical_data = pd.read_csv(file_path)

    historical_data['DurationMinutes'] = historical_data['Sum af TotalDurationInMilliseconds'].apply(convert_milliseconds_to_minutes).round(2)
    historical_data['QueueDurationMinutes'] = historical_data['Sum af EventDurationInMilliseconds'].apply(convert_milliseconds_to_minutes).round(2)
    historical_data['StartTimeDenmark'] = historical_data['StartTimeUtc'].apply(convert_to_denmark_time)

    historical_data['StartTimeDenmark'] = pd.to_datetime(historical_data['StartTimeDenmark'])

    return historical_data
