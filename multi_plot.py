#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import datetime
import calendar
import pathlib
import statistics
import pandas as pd
import numpy as np
import seaborn
import matplotlib.pyplot as plt
from activity import Activity, create_activity, parse_activities_csv, build_activity_dataframe

def ride_heatmap(arguments):
    rides = parse_activities_csv(type_filter="Ride")

    current_datetime = datetime.datetime.now()
    rides = [ride for ride in rides if ride.date.year == current_datetime.year]

    weekday_df = pd.DataFrame(data={
        "weekday": [ride.date.weekday() for ride in rides],
        "week_of_year": [ride.date.strftime("%U") for ride in rides],
        "distance": [ride.distance for ride in rides]
    })
    weekday_pivot = weekday_df.pivot(index="weekday", columns="week_of_year", values="distance")

    plt.clf()
    seaborn.set_theme()
    # ride_plot = seaborn.heatmap(weekday_pivot,
    #     linewidths=0.75,
    #     cbar_kws={"orientation": "horizontal"})
    
    # figure, axes = plt.subplots()
    grid_kws = {"height_ratios": (.9, .05), "hspace": .3}
    f, (ax, cbar_ax) = plt.subplots(2, gridspec_kw=grid_kws)
    ax = seaborn.heatmap(weekday_pivot,
        ax=ax,
        cbar_ax=cbar_ax,
        linewidths=1.0,
        cbar_kws={"orientation": "horizontal"},
        square=True)

    pathlib.Path("plot").mkdir(exist_ok=True)
    plt.savefig(os.path.join("plot", "ride_heatmap.svg"))

    if arguments.show:
        plt.show()


def average_distance_over_weekday(arguments):
    rides = parse_activities_csv(type_filter="Ride")

    weekdays_by_index = dict(zip(range(7), calendar.day_name))
    distances_by_index = dict(zip(range(7), [[] for x in range(7)]))
    for activity in rides:
        distances_by_index[activity.date.weekday()].append(activity.distance)

    average_distances = [statistics.mean(weekday_distances) for index, weekday_distances in distances_by_index.items()]

    adow_df = pd.DataFrame(data={
        "weekday": [weekdays_by_index[index] for index, distance in enumerate(average_distances)],
        "distances": average_distances
    })
    
    plt.clf()
    seaborn.set_theme()
    adow_plot = seaborn.barplot(x="weekday", y="distances", data=adow_df)
    adow_plot.set(xlabel="Day of Week", ylabel="Average Distance (miles)")

    pathlib.Path("plot").mkdir(exist_ok=True)
    plt.savefig(os.path.join("plot", "adow.svg"))
    
    if arguments.show:
        plt.show()


def elevation_time_speed(arguments):
    activities = parse_activities_csv(type_filter="Ride")

    ets_df = pd.DataFrame(data={
        "elevation": [float(activity.elevation_gain) for activity in rides],
        "moving_time": [float(activity.moving_time) / 60 for activity in rides],
        "average_speed": [float(activity.average_speed) * 2.237 if activity.average_speed else 0 for activity in rides]
    })

    plt.clf()
    seaborn.set_theme()
    ets_pivot = pd.pivot_table(ets_df, index="elevation", columns="moving_time", values="average_speed", aggfunc=np.average)
    f, ax = plt.subplots(figsize=(9, 6))
    ets_plot = seaborn.heatmap(ets_pivot, annot=True, linewidths=0.5, ax=ax)

    pathlib.Path("plot").mkdir(exist_ok=True)
    plt.savefig(os.path.join("plot", "ets.svg"))
    
    if arguments.show:
        plt.show()


def average_speed_over_activities(arguments):
    rides = parse_activities_csv(type_filter="Ride")

    asot_df = pd.DataFrame(data={
        "activity_date": [activity.date for activity in rides],
        "average_speed": [activity.average_speed if activity.average_speed else 0 for activity in rides]
    })

    plt.clf()
    seaborn.set_theme()
    asot_plot = seaborn.lineplot(x="activity_date", y="average_speed", data=asot_df)
    asot_plot.set(xlabel="Date", ylabel="Average Speed (mph)")
    plt.fill_between(asot_df.activity_date.values, asot_df.average_speed.values)

    pathlib.Path("plot").mkdir(exist_ok=True)
    plt.savefig(os.path.join("plot", "asot.svg"))
    
    if arguments.show:
        plt.show()


def distance_over_time(arguments):
    """Do a basic scatterplot of distance over ride time."""
    rides = parse_activities_csv(type_filter="Ride")

    dot_by_id = {
        "distance": [ride.distance for ride in rides],
        "moving_time": [ride.moving_time / 60 for ride in rides],
        "average_speed": [ride.average_speed for ride in rides]
    }

    plt.clf()
    seaborn.set_theme()
    dot_df = pd.DataFrame(data=dot_by_id)
    dot_plot = seaborn.lmplot(x="moving_time", y="distance", data=dot_df)
    dot_plot.set(xlabel="Moving Time (Minutes)", ylabel="Distance (Miles)")

    pathlib.Path("plot").mkdir(exist_ok=True)
    plt.savefig(os.path.join("plot", "dot.svg"))

    if arguments.show:
        plt.show()


def distance_histogram(arguments):
    rides = parse_activities_csv(type_filter="Ride")

    distance_df = pd.DataFrame(data={
        "distance": [ride.distance for ride in rides]
    })
    
    plt.clf()
    seaborn.set_theme()
    distance_plot = seaborn.displot(distance_df, x="distance", binwidth=1)
    distance_plot.set(xlabel="Distance (miles)", ylabel="Count")
    plt.title("Distribution of Ride Distances")

    pathlib.Path("plot").mkdir(exist_ok=True)
    plt.savefig(os.path.join("plot", "dhist.svg"))
    
    if arguments.show:
        plt.show()


def moving_time_histogram(arguments):
    rides = parse_activities_csv(type_filter="Ride")

    time_df = pd.DataFrame(data={
        "moving_time": [ride.moving_time / 60 for ride in rides]
    })

    plt.clf()
    seaborn.set_theme()
    time_plot = seaborn.displot(time_df, x="moving_time", binwidth=5)
    time_plot.set(xlabel="Moving Time (minutes)", ylabel="Count")
    plt.title("Distribution of Ride Times")

    pathlib.Path("plot").mkdir(exist_ok=True)
    plt.savefig(os.path.join("plot", "thist.svg"))
    
    if arguments.show:
        plt.show()
