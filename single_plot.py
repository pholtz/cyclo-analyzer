#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import datetime
import pathlib
import gpxpy
import pandas as pd
import seaborn
import matplotlib.pyplot as plt
from activity import Activity, create_activity, parse_activities_csv
from crunch import select_activity

def latlong(arguments):
    """Plot an abstract plot of latitude/longitude scraped from the gpx data."""
    rides = parse_activities_csv(type_filter="Ride")
    selected_activity = select_activity(rides, arguments.date)

    with open("export/" + selected_activity.filename, "r") as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    trackpoints = []
    for track in gpx.tracks:
        for segment in track.segments:
            for index, point in enumerate(segment.points):
                time = datetime.datetime.fromisoformat(point.time.isoformat())
                trackpoints.append((time, point.latitude, point.longitude, point.elevation))

    latlong_dataframe = pd.DataFrame(data={
        "time": [point[0] for point in trackpoints],
        "latitude": [point[1] for point in trackpoints],
        "longitude": [point[2] for point in trackpoints],
        "elevation": [point[3] for point in trackpoints]
    })

    plt.clf()
    seaborn.set_theme(context="paper", style="white")
    seaborn.despine()
    latlong_plot = seaborn.lineplot(x="latitude", y="longitude", data=latlong_dataframe,
        sort=False, estimator=None, ci=None)
    latlong_plot.set(xlabel="", ylabel="")

    pathlib.Path("plot").mkdir(exist_ok=True)
    plt.savefig(os.path.join("plot", "latlong.svg"))

    if arguments.show:
        plt.show()


def speed_over_time(arguments):
    rides = parse_activities_csv(type_filter="Ride")
    selected_activity = select_activity(rides, arguments.date)
    
    with open("export/" + selected_activity.filename, "r") as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    trackpoints = []
    times_and_speeds = []
    for track in gpx.tracks:
        for segment in track.segments:
            for index, point in enumerate(segment.points):
                time = datetime.datetime.fromisoformat(point.time.isoformat())
                speed = 0
                if index < len(segment.points) - 1:
                    speed = point.speed_between(segment.points[index + 1])
                times_and_speeds.append((time, speed * 2.23694))

    speed_dataframe = pd.DataFrame(data={
        "datetime": [point[0] for point in times_and_speeds],
        "speed": [point[1] for point in times_and_speeds]
    })
    speed_dataframe["bin_speed"] = speed_dataframe.rolling(window=15).mean()

    plt.clf()
    seaborn.set_theme()
    avg_plot = seaborn.lineplot(x="datetime", y="bin_speed", data=speed_dataframe)
    avg_plot.set(xlabel="Time", ylabel="Speed (miles / hour)")
    plt.fill_between(speed_dataframe.datetime.values, speed_dataframe.bin_speed.values)
    plt.title("Speed over Time")

    pathlib.Path("plot").mkdir(exist_ok=True)
    plt.savefig(os.path.join("plot", "speed.svg"))
    
    if arguments.show:
        plt.show()


def elevation_over_time(arguments):
    rides = parse_activities_csv(type_filter="Ride")
    selected_activity = select_activity(rides, arguments.date)

    with open("export/" + selected_activity.filename, "r") as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    trackpoints = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                trackpoints.append((datetime.datetime.fromisoformat(point.time.isoformat()), point.elevation))

    elevation_dataframe = pd.DataFrame(data={
        "datetime": [point[0] for point in trackpoints],
        "elevation": [point[1] for point in trackpoints]
    })

    plt.clf()
    seaborn.set_theme()
    elevation_plot = seaborn.lineplot(
        x="datetime", y="elevation", data=elevation_dataframe)
    elevation_plot.set(xlabel="Time", ylabel="Elevation (meters)")
    elevation_plot.axes.set_ylim(elevation_dataframe.elevation.min(), elevation_dataframe.elevation.max())
    plt.fill_between(elevation_dataframe.datetime.values, elevation_dataframe.elevation.values)
    plt.title("Elevation over Time")

    pathlib.Path("plot").mkdir(exist_ok=True)
    plt.savefig(os.path.join("plot", "elevation.svg"))
    
    if arguments.show:
        plt.show()
