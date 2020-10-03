#!/usr/bin/env python
# -*- coding: utf-8 -*-

from activity import Activity, create_activity, parse_activities_csv

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
