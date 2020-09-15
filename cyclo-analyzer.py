#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import csv
import gpxpy
import statistics
import datetime
import pandas as pd
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

    dot_command = subparsers.add_parser("dot")
    dot_command.set_defaults(func=distance_over_time)

    elevation_command = subparsers.add_parser("elevation")
    elevation_command.add_argument("--date", help="search and report activities on this date")
    elevation_command.set_defaults(func=elevation_over_time)

    asot_command = subparsers.add_parser("asot")
    asot_command.set_defaults(func=average_speed_over_activities)

    arguments = parser.parse_args()
    if hasattr(arguments, "func"):
        arguments.func(arguments)
    else:
        parser.print_help()


def average_speed_over_activities(arguments):
    activities = parse_activities_csv()

    asot_df = pd.DataFrame(data={
        "activity_date": [datetime.datetime.strptime(activity.date, "%b %d, %Y, %I:%M:%S %p") for activity in activities],
        "average_speed": [float(activity.average_speed) if activity.average_speed else 0 for activity in activities]
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
