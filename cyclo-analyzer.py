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
from activity import Activity, create_activity

# Yeah, you could hit the api for everything
# You'd have to deal with oauth
# You'd also have to deal with rate limiting
# OR
# You could just take the data export that strava offers as input
# And provide riders aggregated metrics from the .csv and .gpx data instead

# {'activity_id': '2943975776', 'date': 'Dec 19, 2019, 10:32:35 PM', 'name': 'After work after dark quickie', 'activity_type': 'Ride', 'elapsed_time': '1044.0', 'distance': '4058.0', 'filename': 'activities/2943975776.gpx', 'moving_time': '925.0', 'max_speed': '10.0', 'average_speed': '4.387027263641357', 'elevation_gain': '59.79328918457031', 'elevation_low': '115.5', 'elevation_high': '143.3000030517578', 'max_grade': '16.299999237060547', 'average_grade': '0.004928536247462034', 'perceived_exertion': '', 'perceived_relative_effort': ''}

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='reports',
        description='available reports',
        help='')

    baseline_command = subparsers.add_parser("baseline")
    baseline_command.set_defaults(func=baseline)

    dot_command = subparsers.add_parser("dot")
    dot_command.set_defaults(func=distance_over_time)

    elevation_command = subparsers.add_parser("elevation")
    elevation_command.add_argument("--date", help="search and report activities on this date")
    elevation_command.set_defaults(func=elevation_over_time)

    asot_command = subparsers.add_parser("asot")
    asot_command.set_defaults(func=average_speed_over_activities)

    ets_command = subparsers.add_parser("ets")
    ets_command.set_defaults(func=elevation_time_speed)

    adow_command = subparsers.add_parser("adow")
    adow_command.set_defaults(func=average_distance_over_weekday)

    arguments = parser.parse_args()
    if hasattr(arguments, "func"):
        arguments.func(arguments)
    else:
        parser.print_help()


def baseline(arguments):
    activities = parse_activities_csv()
    rides = [activity for activity in activities if activity.activity_type == "Ride"]

    first_datetime = datetime.datetime.strptime(rides[0].date, "%b %d, %Y, %I:%M:%S %p")
    last_datetime = datetime.datetime.strptime(rides[-1].date, "%b %d, %Y, %I:%M:%S %p")

    ride_names = [ride.name for ride in rides]
    ride_dates = [datetime.datetime.strptime(ride.date, "%b %d, %Y, %I:%M:%S %p") for ride in rides]
    date_df = pd.DataFrame(data={
        "name": ride_names,
        "date": ride_dates
    })
    rides_by_week = date_df.groupby(pd.Grouper(key="date", freq="W"))
    average_rides_per_week = statistics.mean([len(weekly_rides[1]) for weekly_rides in rides_by_week])
    
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
        distance = float(ride.distance)
        elevation = float(ride.elevation_gain)
        moving_time = float(ride.moving_time)
        if not min_distance or distance < min_distance:
            min_distance = distance
        if not max_distance or distance > max_distance:
            max_distance = distance
        if not min_elevation or elevation < min_elevation:
            min_elevation = elevation
        if not max_elevation or elevation > max_elevation:
            max_elevation = elevation
        if not min_time or moving_time < min_time:
            min_time = moving_time
        if not max_time or moving_time > max_time:
            max_time = moving_time
        total_distance += distance
        total_elevation += elevation
        total_time += moving_time

    min_distance_miles = round(min_distance * 0.000621371, 2)
    max_distance_miles = round(max_distance * 0.000621371, 2)
    average_distance_miles = round(total_distance / len(rides) * 0.000621371, 2)

    min_elevation_feet = round(min_elevation * 3.28084, 2)
    max_elevation_feet = round(max_elevation * 3.28084, 2)
    average_elevation_feet = round(total_elevation / len(rides) * 3.28084, 2)

    min_time_minutes = round(min_time / 60, 2)
    max_time_minutes = round(max_time / 60, 2)
    average_time_minutes = round(total_time / len(rides) / 60, 2)

    total_distance_miles = round(total_time * 0.000621371, 2)
    total_elevation_feet = round(total_elevation * 3.28084, 2)
    total_time_hours = round(total_time / 3600, 2)

    print("Ride Count: {}".format(len(rides)))
    print("Date Range: {} - {}".format(first_datetime.strftime("%b %d %Y"), last_datetime.strftime("%b %d %Y")))
    print("\n{}\n".format("=" * 30))
    print("Distances: {} (min) {} (max) {} (avg) miles".format(min_distance_miles, max_distance_miles, average_distance_miles))
    print("Elevation: {} (min) {} (max) {} (avg) feet".format(min_elevation_feet, max_elevation_feet, average_elevation_feet))
    print("Moving Time: {} (min) {} (max) {} (avg) minutes".format(min_time_minutes, max_time_minutes, average_time_minutes))
    print("\n{}\n".format("=" * 30))
    print("Total Distance: {} miles".format(total_distance_miles))
    print("Total Elevation Gain: {} feet".format(total_elevation_feet))
    print("Total Time: {} hours".format(total_time_hours))
    print("\n{}\n".format("=" * 30))
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

    selected_activity = activities[0]
    if arguments.date:
        desired_datetime = datetime.datetime.fromisoformat(arguments.date)
        for activity in activities:
            activity_datetime = datetime.datetime.strptime(activity.date, "%b %d, %Y, %I:%M:%S %p")
            if desired_datetime.year == activity_datetime.year and \
                    desired_datetime.month == activity_datetime.month and \
                    desired_datetime.day == activity_datetime.day:
                selected_activity = activity
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


def distance_over_time(arguments):
    activities = parse_activities_csv()

    # Do a basic avg distance calc across dataset
    average_distance_meters = statistics.mean(
        [float(activity.distance) for activity in activities])
    average_distance_miles = average_distance_meters * 0.000621371
    print("Average Distance -> {} miles".format(average_distance_miles))

    # Do a basic scatterplot of distance over ride time
    dot_by_id = {
        "distance": [float(activity.distance) * 0.000621371 for activity in activities],
        "moving_time": [float(activity.moving_time) / 60 for activity in activities]
    }
    dot_df = pd.DataFrame(data=dot_by_id)
    dot_plot = seaborn.relplot(x="moving_time", y="distance", data=dot_df)
    dot_plot.set(xlabel="Moving Time (Minutes)", ylabel="Distance (Miles)")
    plt.savefig("dot.png")
    # plt.show()


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


if __name__ == '__main__':
    main()
