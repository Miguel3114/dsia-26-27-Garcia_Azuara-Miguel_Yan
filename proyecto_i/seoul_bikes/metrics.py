import pandas as pd


def total_rentals(df):
    return df["rented_bike_count"].sum()

def average_rentals_by_season(df):
    return df.groupby("season")["rented_bike_count"].mean().to_dict()

def average_rentals_by_hour(df):
    return df.groupby("hour")["rented_bike_count"].mean().to_dict()

def average_rentals_by_holiday(df):
    return (df.groupby("holiday")["rented_bike_count"].mean().to_dict())