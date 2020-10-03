#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import textwrap
import baseline
import single_metrics
import multi_metrics
import miscellaneous_metrics

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
    stats_command.set_defaults(func=baseline.stats)

    ### Single Ride Metrics ###
    elevation_command = subparsers.add_parser("elevation",
        help="Plot elevation as a function of time for a single ride (area)")
    elevation_command.add_argument("--date", help="search and report activities on this date")
    elevation_command.set_defaults(func=single_metrics.elevation_over_time)

    speed_command = subparsers.add_parser("speed",
        help="Plot speed as a function of time for a single ride (area)")
    speed_command.add_argument("--date", help="search and report activities on this date")
    speed_command.set_defaults(func=single_metrics.speed_over_time)

    ### Aggregated Metrics ###
    dot_command = subparsers.add_parser("dot",
        help="Plot distance as a function of moving time (scatter)")
    dot_command.set_defaults(func=multi_metrics.distance_over_time)

    asot_command = subparsers.add_parser("asot",
        help="Plot average speed as a function of time (area)")
    asot_command.set_defaults(func=multi_metrics.average_speed_over_activities)

    ets_command = subparsers.add_parser("ets",
        help="Plot relationship between elevation, moving time, and speed (heatmap)")
    ets_command.set_defaults(func=multi_metrics.elevation_time_speed)

    adow_command = subparsers.add_parser("adow",
        help="Plot average distances for each day of the week (bar)")
    adow_command.set_defaults(func=multi_metrics.average_distance_over_weekday)

    distance_histogram_command = subparsers.add_parser("dhist",
        help="Plot the distribution of ride distances for all time")
    distance_histogram_command.set_defaults(func=multi_metrics.distance_histogram)

    moving_time_histogram_command = subparsers.add_parser("thist",
        help="Plot the distribution of ride times for all time")
    moving_time_histogram_command.set_defaults(func=multi_metrics.moving_time_histogram)

    ### Miscellaneous ###
    dump_command = subparsers.add_parser("dump",
        help="Applies a specified transform to the activities file, for readability or compatibility with another system")
    dump_command.set_defaults(func=miscellaneous_metrics.dump)

    arguments = parser.parse_args()
    if hasattr(arguments, "func"):
        arguments.func(arguments)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
