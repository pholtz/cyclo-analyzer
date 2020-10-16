#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import textwrap
import baseline
import single_plot
import multi_plot
import transform
import report
import locale

def main():
    locale.setlocale(locale.LC_ALL, '')
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

    ### Report Generators ###
    report_one_command = subparsers.add_parser("report",
        help="Generate a report for a single activity")
    report_one_command.add_argument("--date", help="seach and report activities on this date (yyyy-mm-dd)")
    report_one_command.set_defaults(func=report.generate_single_report)

    report_all_command = subparsers.add_parser("report-all",
        help="Generate a report of aggregated activity metrics")
    report_all_command.set_defaults(func=report.generate_aggregate_report)

    ### Single Activity Plots ###
    elevation_command = subparsers.add_parser("elevation",
        help="Plot elevation as a function of time for a single ride (area)")
    elevation_command.add_argument("--date", help="search and report activities on this date (yyyy-mm-dd)")
    elevation_command.add_argument("--show", action="store_true", help="use matplotlib to display plot")
    elevation_command.set_defaults(func=single_plot.elevation_over_time)

    speed_command = subparsers.add_parser("speed",
        help="Plot speed as a function of time for a single ride (area)")
    speed_command.add_argument("--date", help="search and report activities on this date (yyyy-mm-dd)")
    speed_command.add_argument("--show", action="store_true", help="use matplotlib to display plot")
    speed_command.set_defaults(func=single_plot.speed_over_time)

    latlong_command = subparsers.add_parser("latlong",
        help="Plot latitude / longitude of segments without any reference points")
    latlong_command.add_argument("--date", help="search and report activities on this date (yyyy-mm-dd)")
    latlong_command.add_argument("--show", action="store_true", help="use matplotlib to display plot")
    latlong_command.set_defaults(func=single_plot.latlong)

    ### Aggregated Activity Plots ###
    dot_command = subparsers.add_parser("dot",
        help="Plot distance as a function of moving time (scatter)")
    dot_command.add_argument("--show", action="store_true", help="use matplotlib to display plot")
    dot_command.set_defaults(func=multi_plot.distance_over_time)

    asot_command = subparsers.add_parser("asot",
        help="Plot average speed as a function of time (area)")
    asot_command.add_argument("--show", action="store_true", help="use matplotlib to display plot")
    asot_command.set_defaults(func=multi_plot.average_speed_over_activities)

    ets_command = subparsers.add_parser("ets",
        help="Plot relationship between elevation, moving time, and speed (heatmap)")
    ets_command.add_argument("--show", action="store_true", help="use matplotlib to display plot")
    ets_command.set_defaults(func=multi_plot.elevation_time_speed)

    ride_command = subparsers.add_parser("ride",
        help="Plot ride activity heatmap for the calendar year")
    ride_command.add_argument("--show", action="store_true", help="use matplotlib to display plot")
    ride_command.set_defaults(func=multi_plot.ride_heatmap)

    adow_command = subparsers.add_parser("adow",
        help="Plot average distances for each day of the week (bar)")
    adow_command.add_argument("--show", action="store_true", help="use matplotlib to display plot")
    adow_command.set_defaults(func=multi_plot.average_distance_over_weekday)

    distance_histogram_command = subparsers.add_parser("dhist",
        help="Plot the distribution of ride distances for all time")
    distance_histogram_command.add_argument("--show", action="store_true", help="use matplotlib to display plot")
    distance_histogram_command.set_defaults(func=multi_plot.distance_histogram)

    moving_time_histogram_command = subparsers.add_parser("thist",
        help="Plot the distribution of ride times for all time")
    moving_time_histogram_command.add_argument("--show", action="store_true", help="use matplotlib to display plot")
    moving_time_histogram_command.set_defaults(func=multi_plot.moving_time_histogram)

    ### Transform ###
    dump_command = subparsers.add_parser("dump",
        help="Applies a specified transform to the activities file, for readability or compatibility with another system")
    dump_command.set_defaults(func=transform.dump)

    arguments = parser.parse_args()
    if hasattr(arguments, "func"):
        arguments.func(arguments)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
