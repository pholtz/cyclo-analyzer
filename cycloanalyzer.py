#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import csv
import gpxpy
import statistics
import datetime
import calendar
import pandas as pd
import numpy as np
import seaborn
import matplotlib.pyplot as plt
import textwrap
import pathlib
from activity import Activity, create_activity, parse_activities_csv
from baseline import stats
from single_metrics import speed_over_time, elevation_over_time

def main():
    parser = argparse.ArgumentParser(description=textwrap.dedent(
        """\
        Analyze a provided activities archive.
        Note: Currently supports only strava activity extracts. 
        """))
    subparsers = parser.add_subparsers(title="reports",
        description="available reports",
        help="")

    ### Statistics ###
    stats_command = subparsers.add_parser("stats",
        aliases=["stat", "statistics", "baseline"],
        help="Print a textual report of aggregated data scraped from the activity file")
    stats_command.set_defaults(func=stats)

    ### Single Ride Metrics ###
    elevation_command = subparsers.add_parser("elevation",
        help="Plot elevation as a function of time for a single ride (area)")
    elevation_command.add_argument("--date", help="search and report activities on this date")
    elevation_command.set_defaults(func=elevation_over_time)

    speed_command = subparsers.add_parser("speed",
        help="Plot speed as a function of time for a single ride (area)")
    speed_command.add_argument("--date", help="search and report activities on this date")
    speed_command.set_defaults(func=speed_over_time)

    ### Aggregated Metrics ###
    dot_command = subparsers.add_parser("dot",
        help="Plot distance as a function of moving time (scatter)")
    dot_command.set_defaults(func=distance_over_time)

    asot_command = subparsers.add_parser("asot",
        help="Plot average speed as a function of time (area)")
    asot_command.set_defaults(func=average_speed_over_activities)

    ets_command = subparsers.add_parser("ets",
        help="Plot relationship between elevation, moving time, and speed (heatmap)")
    ets_command.set_defaults(func=elevation_time_speed)

    adow_command = subparsers.add_parser("adow",
        help="Plot average distances for each day of the week (bar)")
    adow_command.set_defaults(func=average_distance_over_weekday)

    distance_histogram_command = subparsers.add_parser("dhist",
        help="Plot the distribution of ride distances for all time")
    distance_histogram_command.set_defaults(func=distance_histogram)

    moving_time_histogram_command = subparsers.add_parser("thist",
        help="Plot the distribution of ride times for all time")
    moving_time_histogram_command.set_defaults(func=moving_time_histogram)

    ### Miscellaneous ###
    dump_command = subparsers.add_parser("dump",
        help="Applies a specified transform to the activities file, for readability or compatibility with another system")
    dump_command.set_defaults(func=dump)

    arguments = parser.parse_args()
    if hasattr(arguments, "func"):
        arguments.func(arguments)
    else:
        parser.print_help()


def average_distance_over_weekday(arguments):
    activities = parse_activities_csv()
    rides = [activity for activity in activities if activity.activity_type == "Ride"]

    weekdays_by_index = dict(zip(range(7), calendar.day_name))
    distances_by_index = dict(zip(range(7), [[] for x in range(7)]))
    for activity in rides:
        distances_by_index[activity.date.weekday()].append(float(activity.distance) * 0.000621371)

    average_distances = [statistics.mean(weekday_distances) for index, weekday_distances in distances_by_index.items()]

    adow_df = pd.DataFrame(data={
        "weekday": [weekdays_by_index[index] for index, distance in enumerate(average_distances)],
        "distances": average_distances
    })
    
    seaborn.set_theme()
    adow_plot = seaborn.barplot(x="weekday", y="distances", data=adow_df)
    adow_plot.set(xlabel="Day of Week", ylabel="Average Distance (miles)")
    plt.savefig("adow.png")
    plt.show()


def elevation_time_speed(arguments):
    activities = parse_activities_csv()

    rides = [activity for activity in activities if activity.activity_type == "Ride"]
    print("Filtered {} activities down to {} Ride activities".format(len(activities), len(rides)))

    ets_df = pd.DataFrame(data={
        "elevation": [float(activity.elevation_gain) for activity in rides],
        "moving_time": [float(activity.moving_time) / 60 for activity in rides],
        "average_speed": [float(activity.average_speed) * 2.237 if activity.average_speed else 0 for activity in rides]
    })

    seaborn.set_theme()
    ets_pivot = pd.pivot_table(ets_df, index="elevation", columns="moving_time", values="average_speed", aggfunc=np.average)
    f, ax = plt.subplots(figsize=(9, 6))
    ets_plot = seaborn.heatmap(ets_pivot, annot=True, linewidths=0.5, ax=ax)
    plt.savefig("ets.png")
    plt.show()


def average_speed_over_activities(arguments):
    activities = parse_activities_csv()
    rides = [activity for activity in activities if activity.activity_type == "Ride"]
    rides = [ride.convert_to_imperial() for ride in rides]

    asot_df = pd.DataFrame(data={
        "activity_date": [activity.date for activity in rides],
        "average_speed": [activity.average_speed if activity.average_speed else 0 for activity in rides]
    })

    seaborn.set_theme()
    asot_plot = seaborn.lineplot(x="activity_date", y="average_speed", data=asot_df)
    asot_plot.set(xlabel="Date", ylabel="Average Speed (mph)")
    plt.fill_between(asot_df.activity_date.values, asot_df.average_speed.values)
    plt.savefig("asot.png")
    plt.show()


def distance_over_time(arguments):
    """Do a basic scatterplot of distance over ride time"""
    activities = parse_activities_csv()
    rides = [activity for activity in activities if activity.activity_type == "Ride"]
    rides = [ride.convert_to_imperial() for ride in rides]

    dot_by_id = {
        "distance": [ride.distance for ride in rides],
        "moving_time": [ride.moving_time / 60 for ride in rides],
        "average_speed": [ride.average_speed for ride in rides]
    }

    seaborn.set_theme()
    dot_df = pd.DataFrame(data=dot_by_id)
    dot_plot = seaborn.lmplot(x="moving_time", y="distance", data=dot_df)
    dot_plot.set(xlabel="Moving Time (Minutes)", ylabel="Distance (Miles)")
    plt.savefig("dot.png")
    plt.show()


def distance_histogram(arguments):
    activities = parse_activities_csv()
    rides = [activity for activity in activities if activity.activity_type == "Ride"]
    rides = [ride.convert_to_imperial() for ride in rides]

    distance_df = pd.DataFrame(data={
        "distance": [ride.distance for ride in rides]
    })
    
    seaborn.set_theme()
    distance_plot = seaborn.displot(distance_df, x="distance", binwidth=1)
    distance_plot.set(xlabel="Distance (miles)", ylabel="Count")
    plt.savefig("dhist.svg")
    plt.show()


def moving_time_histogram(arguments):
    activities = parse_activities_csv()
    rides = [activity for activity in activities if activity.activity_type == "Ride"]
    rides = [ride.convert_to_imperial() for ride in rides]

    time_df = pd.DataFrame(data={
        "moving_time": [ride.moving_time / 60 for ride in rides]
    })

    seaborn.set_theme()
    time_plot = seaborn.displot(time_df, x="moving_time", binwidth=5)
    time_plot.set(xlabel="Moving Time (minutes)", ylabel="Count")
    plt.savefig("thist.svg")
    plt.show()


def dump(arguments):
    """Output a manipulated version of the activities.csv file.
    Take optional arguments specifying the shape of the output.
    """
    activities = parse_activities_csv()
    activities = [activity.convert_to_imperial() for activity in activities]

    # Default view is just a linefeed separated print of each activity, date ascending
    for activity in activities:
        print("Date: {}".format(activity.date))
        print("Name: {}".format(activity.name))
        print("Type: {}".format(activity.activity_type))
        print("Moving Time: {} minutes".format(round(activity.moving_time / 60, 2)))
        print("Distance: {} miles".format(round(activity.distance, 2)))
        print("Elevation Gain: {} feet".format(round(activity.elevation_gain, 2)))
        print("Average Speed: {} mph".format(round(activity.average_speed, 2)))
        print("\n")


if __name__ == '__main__':
    main()
