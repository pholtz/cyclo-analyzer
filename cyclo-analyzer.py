#!/usr/bin/env python
# -*- coding: utf-8 -*-

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


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='reports', description='available reports', help='')

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
    
    min_distance_ride = min(rides, key=lambda x: float(x.distance) * 0.000621371)
    max_distance_ride = max(rides, key=lambda x: float(x.distance) * 0.000621371)
    min_distance = round(float(min_distance_ride.distance) * 0.000621371, 2)
    max_distance = round(float(max_distance_ride.distance) * 0.000621371, 2)
    average_distance_meters = statistics.mean([float(activity.distance) for activity in activities])
    average_distance_miles = round(average_distance_meters * 0.000621371, 2)

    min_elevation_ride = min(rides, key=lambda x: float(x.elevation_gain))
    max_elevation_ride = max(rides, key=lambda x: float(x.elevation_gain))
    min_elevation_feet = round(float(min_elevation_ride.elevation_gain) * 3.28084, 2)
    max_elevation_feet = round(float(max_elevation_ride.elevation_gain) * 3.28084, 2)
    average_elevation = statistics.mean([float(activity.elevation_gain) for activity in activities])
    average_elevation_feet = round(average_elevation * 3.28084, 2)

    print("Ride Count: {}".format(len(rides)))
    print("Date Range: {} - {}".format(first_datetime.strftime("%b %d %Y"), last_datetime.strftime("%b %d %Y")))
    print("Distances: {} (min) {} (max) {} (avg) miles".format(min_distance, max_distance, average_distance_miles))
    print("Elevations: {} (min) {} (max) {} (avg) feet".format(min_elevation_feet, max_elevation_feet, average_elevation_feet))


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
