#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import datetime
import pathlib
import gpxpy
import pandas as pd
import statistics
import seaborn
import matplotlib.pyplot as plt
from activity import Activity, create_activity, parse_activities_csv

def select_activity(activities, iso_date=None):
    """Given a list of activities and selection criteria, return the first activity which matches the criteria. 
    If no matching activity can be found, or selection criteria was not provided, simply return the most recent 
    activity.
    """
    selected_activity = activities[-1]
    if iso_date:
        desired_datetime = datetime.datetime.fromisoformat(iso_date)
        for activity in activities:
            if desired_datetime.year == ride.date.year and \
                    desired_datetime.month == ride.date.month and \
                    desired_datetime.day == ride.date.day:
                selected_activity = activity
                break
    print("Selected activity \"{}\" on {}".format(selected_activity.name, selected_activity.date))
    return selected_activity


def crunch_total_metrics(rides):
    total_distance = 0
    total_elevation = 0
    total_time = 0

    for ride in rides:
        total_distance += ride.distance
        total_elevation += ride.elevation_gain
        total_time += ride.moving_time

    total_distance = round(total_distance, 2)
    total_elevation = round(total_elevation, 2)
    total_time_hours = round(total_time / 3600, 2)
    return (len(rides), total_time_hours, total_distance, total_elevation)


def crunch_weekly_metrics(rides):
    """Given activities, calculate and return several "by week" averages."""
    ride_names = [ride.name for ride in rides]
    ride_dates = [ride.date for ride in rides]
    ride_moving_times = [ride.moving_time for ride in rides]
    ride_distances = [ride.distance for ride in rides]
    date_df = pd.DataFrame(data={
        "name": ride_names,
        "date": ride_dates,
        "moving_time": ride_moving_times,
        "distance": ride_distances
    })
    rides_by_week = date_df.groupby(pd.Grouper(key="date", freq="W"))
    average_rides_per_week = round(statistics.mean([len(weekly_rides[1]) for weekly_rides in rides_by_week]), 2)
    average_time_per_week = round(statistics.mean([sum(weekly_rides[1]["moving_time"] / 60) for weekly_rides in rides_by_week]), 2)
    average_distance_per_week = round(statistics.mean([sum(weekly_rides[1]["distance"]) for weekly_rides in rides_by_week]), 2)
    return (average_rides_per_week, average_time_per_week, average_distance_per_week)
