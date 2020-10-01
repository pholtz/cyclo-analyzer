#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
from activity import Activity, create_activity

# Yeah, you could hit the api for everything
# You'd have to deal with oauth
# You'd also have to deal with rate limiting
# OR
# You could just take the data export that strava offers as input
# And provide riders aggregated metrics from the .csv and .gpx data instead

# {'activity_id': '2943975776', 'date': 'Dec 19, 2019, 10:32:35 PM', 'name': 'After work after dark quickie', 'activity_type': 'Ride', 'elapsed_time': '1044.0', 'distance': '4058.0', 'filename': 'activities/2943975776.gpx', 'moving_time': '925.0', 'max_speed': '10.0', 'average_speed': '4.387027263641357', 'elevation_gain': '59.79328918457031', 'elevation_low': '115.5', 'elevation_high': '143.3000030517578', 'max_grade': '16.299999237060547', 'average_grade': '0.004928536247462034', 'perceived_exertion': '', 'perceived_relative_effort': ''}

def main():
    parser = argparse.ArgumentParser(description=textwrap.dedent(
        """\
        Analyze a provided activities archive.
        Note: Currently supports only strava activity extracts.
        """))
    subparsers = parser.add_subparsers(title="reports",
        description="available reports",
        help="")

    ### Aggregated Metrics ###
    baseline_command = subparsers.add_parser("baseline",
        help="Print a textual report of aggregated data scraped from the activity file")
    baseline_command.set_defaults(func=baseline)

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

    ### Single Ride Metrics ###
    elevation_command = subparsers.add_parser("elevation",
        help="Plot elevation as a function of time for a single ride (area)")
    elevation_command.add_argument("--date", help="search and report activities on this date")
    elevation_command.set_defaults(func=elevation_over_time)

    speed_command = subparsers.add_parser("speed",
        help="Plot speed as a function of time for a single ride (area)")
    speed_command.add_argument("--date", help="search and report activities on this date")
    speed_command.set_defaults(func=speed_over_time)

    ### Miscellaneous ###
    dump_command = subparsers.add_parser("dump",
        help="Applies a specified transform to the activities file, for readability or compatibility with another system")
    dump_command.set_defaults(func=dump)

    arguments = parser.parse_args()
    if hasattr(arguments, "func"):
        arguments.func(arguments)
    else:
        parser.print_help()


def baseline(arguments):
    activities = parse_activities_csv()
    rides = [activity for activity in activities if activity.activity_type == "Ride"]
    rides = [ride.convert_to_imperial() for ride in rides]

    first_datetime = rides[0].date
    last_datetime = rides[-1].date

    ride_names = [ride.name for ride in rides]
    ride_dates = [ride.date for ride in rides]
    date_df = pd.DataFrame(data={
        "name": ride_names,
        "date": ride_dates
    })
    rides_by_week = date_df.groupby(pd.Grouper(key="date", freq="W"))
    average_rides_per_week = round(statistics.mean([len(weekly_rides[1]) for weekly_rides in rides_by_week]), 2)
    
    min_distance = None
    min_elevation = None
    min_time = None
    max_distance = None
    max_elevation = None
    max_time = None
    total_distance = 0
    total_elevation = 0
    total_time = 0

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

    print("Ride Count: {}".format(len(rides)))
    print("Date Range: {} - {}".format(first_datetime.strftime("%b %d %Y"), last_datetime.strftime("%b %d %Y")))
    print("{}".format("=" * 30))
    print("Distances: {} (min) {} (max) {} (avg) miles".format(min_distance, max_distance, average_distance))
    print("Elevation: {} (min) {} (max) {} (avg) feet".format(min_elevation, max_elevation, average_elevation))
    print("Moving Time: {} (min) {} (max) {} (avg) minutes".format(min_time_minutes, max_time_minutes, average_time_minutes))
    print("{}".format("=" * 30))
    print("Total Distance: {} miles".format(total_distance))
    print("Total Elevation Gain: {} feet".format(total_elevation))
    print("Total Time: {} hours".format(total_time))
    print("{}".format("=" * 30))
    print("Average Rides Per Week: {}".format(average_rides_per_week))


def average_distance_over_weekday(arguments):
    activities = parse_activities_csv()
    rides = [activity for activity in activities if activity.activity_type == "Ride"]

    weekdays_by_index = dict(zip(range(7), calendar.day_name))
    distances_by_index = dict(zip(range(7), [[] for x in range(7)]))
    for activity in rides:
        activity_datetime = datetime.datetime.strptime(activity.date, "%b %d, %Y, %I:%M:%S %p")
        distances_by_index[activity_datetime.weekday()].append(float(activity.distance) * 0.000621371)

    average_distances = [statistics.mean(weekday_distances) for index, weekday_distances in distances_by_index.items()]

    adow_df = pd.DataFrame(data={
        "weekday": [weekdays_by_index[index] for index, distance in enumerate(average_distances)],
        "distances": average_distances
    })
    print(adow_df)
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
    ets_pivot = pd.pivot_table(ets_df, index="elevation", columns="moving_time", values="average_speed", aggfunc=np.average)
    f, ax = plt.subplots(figsize=(9, 6))
    ets_plot = seaborn.heatmap(ets_pivot, annot=True, linewidths=0.5, ax=ax)
    plt.savefig("ets.png")
    plt.show()


def average_speed_over_activities(arguments):
    activities = parse_activities_csv()
    
    rides = [activity for activity in activities if activity.activity_type == "Ride"]
    print("Filtered {} activities down to {} Ride activities".format(len(activities), len(rides)))

    asot_df = pd.DataFrame(data={
        "activity_date": [datetime.datetime.strptime(activity.date, "%b %d, %Y, %I:%M:%S %p") for activity in rides],
        "average_speed": [float(activity.average_speed) * 2.237 if activity.average_speed else 0 for activity in rides]
    })
    asot_plot = seaborn.lineplot(x="activity_date", y="average_speed", data=asot_df)
    asot_plot.set(xlabel="Date", ylabel="Average Speed (mph)")
    plt.fill_between(asot_df.activity_date.values, asot_df.average_speed.values)
    plt.savefig("asot.png")
    plt.show()


# TODO: Compare elevations across activities
def elevation_over_time(arguments):
    activities = parse_activities_csv()
    rides = [activity for activity in activities if activity.activity_type == "Ride"]
    rides = [ride.convert_to_imperial() for ride in rides]

    selected_activity = rides[0]
    if arguments.date:
        desired_datetime = datetime.datetime.fromisoformat(arguments.date)
        for ride in rides:
            if desired_datetime.year == ride.date.year and \
                    desired_datetime.month == ride.date.month and \
                    desired_datetime.day == ride.date.day:
                selected_activity = ride
                break

    print("Selected activity {} on {}".format(selected_activity.name, selected_activity.date))
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
    elevation_plot = seaborn.lineplot(
        x="datetime", y="elevation", data=elevation_dataframe)
    elevation_plot.set(xlabel="Time", ylabel="Elevation (meters)")
    plt.fill_between(elevation_dataframe.datetime.values, elevation_dataframe.elevation.values)
    plt.savefig("elevation.png")
    plt.show()


def speed_over_time(arguments):
    activities = parse_activities_csv()
    rides = [activity for activity in activities if activity.activity_type == "Ride"]
    rides = [ride.convert_to_imperial() for ride in rides]

    selected_activity = rides[0]
    if arguments.date:
        desired_datetime = datetime.datetime.fromisoformat(arguments.date)
        for ride in rides:
            if desired_datetime.year == ride.date.year and \
                    desired_datetime.month == ride.date.month and \
                    desired_datetime.day == ride.date.day:
                selected_activity = activity
                break

    print("Selected activity {} on {}".format(selected_activity.name, selected_activity.date))
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
    speed_dataframe["bin_speed"] = speed_dataframe.rolling(window=10).mean()

    avg_palette = seaborn.color_palette("rocket")
    avg_plot = seaborn.lineplot(x="datetime", y="bin_speed", data=speed_dataframe, palette=avg_palette)
    avg_plot.set(xlabel="Time", ylabel="Speed (meters / second)")
    
    # plt.fill_between(speed_dataframe.datetime.values, speed_dataframe.speed.values)
    plt.savefig("speed.png")
    plt.show()


def distance_over_time(arguments):
    """Do a basic scatterplot of distance over ride time"""
    activities = parse_activities_csv()
    rides = [activity for activity in activities if activity.activity_type == "Ride"]
    rides = [ride.convert_to_imperial() for ride in rides]

    dot_by_id = {
        "distance": [ride.distance for ride in rides],
        "moving_time": [ride.moving_time / 60 for ride in rides]
    }
    dot_df = pd.DataFrame(data=dot_by_id)
    dot_plot = seaborn.relplot(x="moving_time", y="distance", data=dot_df)
    dot_plot.set(xlabel="Moving Time (Minutes)", ylabel="Distance (Miles)")
    plt.savefig("dot.png")
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


def parse_activities_csv():
    activities = []
    with open("export/activities.csv", "r") as activities_file:
        activities_reader = csv.DictReader(activities_file)
        for activity_record in activities_reader:
            activities.append(create_activity(activity_record))
    return activities


def parse_activities_json():
    activities = []
    with open("activities.json", "r") as activities_file:
        activities = json.load(activities_file)
    print("Retrieved {} activities".format(len(activities)))

    for activity in activities:
        print("{} -> {} total meters, {} moving seconds, {} elevation meters".format(
            activity["name"], activity["distance"], activity["moving_time"], activity["total_elevation_gain"]))


def the_cooler_dump(obj):
    for attr in dir(obj):
        print("obj.%s = %r" % (attr, getattr(obj, attr)))


if __name__ == '__main__':
    main()
