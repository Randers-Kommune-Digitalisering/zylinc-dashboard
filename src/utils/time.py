import pandas as pd
from datetime import timedelta


def convert_minutes_to_hms(minutes):
    if pd.isna(minutes):
        return "0:00:00"
    seconds = int(minutes * 60)
    return str(timedelta(seconds=seconds))
