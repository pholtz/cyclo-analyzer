#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import pandas as pd
import statistics
import textwrap
from activity import Activity, create_activity, parse_activities_csv

def stats(arguments):
    activities = parse_activities_csv()
    rides = [activity for activity in activities if activity.activity_type == "Ride"]
    rides = [ride.convert_to_imperial() for ride in rides]

    current_datetime = datetime.datetime.now()
    first_datetime = rides[0].date
    last_datetime = rides[-1].date

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
    
    min_distance = None
    min_elevation = None
    min_time = None
    max_distance = None
    max_elevation = None
    max_time = None
    total_distance = 0
    total_elevation = 0
    total_time = 0
    ytd_rides = 0
    ytd_distance = 0
    ytd_elevation = 0
    ytd_time = 0

    for ride in rides:
        if not min_distance or ride.distance < min_distance:
            min_distance = ride.distance
        if not max_distance or ride.distance > max_distance:
            max_distance = ride.distance
        if not min_elevation or ride.elevation_gain < min_elevation:
            min_elevation = ride.elevation_gain
        if not max_elevation or ride.elevation_gain > max_elevation:
            max_elevation = ride.elevation_gain
        if not min_time or ride.moving_time < min_time:
            min_time = ride.moving_time
        if not max_time or ride.moving_time > max_time:
            max_time = ride.moving_time
        total_distance += ride.distance
        total_elevation += ride.elevation_gain
        total_time += ride.moving_time
        if ride.date.year == current_datetime.year:
            ytd_rides += 1
            ytd_distance += ride.distance
            ytd_elevation += ride.elevation_gain
            ytd_time += ride.moving_time

    min_distance = round(min_distance, 2)
    max_distance = round(max_distance, 2)
    average_distance = round(total_distance / len(rides), 2)

    min_elevation = round(min_elevation, 2)
    max_elevation = round(max_elevation, 2)
    average_elevation = round(total_elevation / len(rides), 2)

    min_time_minutes = round(min_time / 60, 2)
    max_time_minutes = round(max_time / 60, 2)
    average_time_minutes = round(total_time / len(rides) / 60, 2)

    total_distance = round(total_distance, 2)
    total_elevation = round(total_elevation, 2)
    total_time_hours = round(total_time / 3600, 2)

    ytd_distance = round(ytd_distance, 2)
    ytd_elevation = round(ytd_elevation, 2)
    ytd_time_hours = round(ytd_time / 3600, 2)

    print(textwrap.dedent("""\
    ###########
    # Overall #
    ###########
    Average Rides Per Week: {}
    Average Time Per Week: {} minutes
    Average Distance Per Week: {} miles
    """.format(average_rides_per_week, average_time_per_week, average_distance_per_week)))

    print(textwrap.dedent("""\
    ################
    # Year To Date #
    ################
    Rides: {}
    Time: {} hours
    Distance: {} miles
    Elevation Gain: {} feet
    """.format(ytd_rides, ytd_time_hours, ytd_distance, ytd_elevation)))

    print(textwrap.dedent("""\
    ############
    # All Time #
    ############
    Rides: {}
    Time: {} hours
    Distance: {} miles
    Elevation Gain: {} feet
    """.format(len(rides), total_time_hours, total_distance, total_elevation)))

    print("Date Range: {} - {}".format(first_datetime.strftime("%b %d %Y"), last_datetime.strftime("%b %d %Y")))
    print("Distances: {} (min) {} (max) {} (avg) miles".format(min_distance, max_distance, average_distance))
    print("Elevation: {} (min) {} (max) {} (avg) feet".format(min_elevation, max_elevation, average_elevation))
    print("Moving Time: {} (min) {} (max) {} (avg) minutes".format(min_time_minutes, max_time_minutes, average_time_minutes))
