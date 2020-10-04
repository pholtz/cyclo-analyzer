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
