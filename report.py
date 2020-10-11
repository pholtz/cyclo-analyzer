#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import calendar
import statistics
import pandas as pd
import seaborn
import pathlib
import matplotlib.pyplot as plt
from jinja2 import Environment, PackageLoader, select_autoescape
from activity import Activity, create_activity, parse_activities_csv
import crunch
import single_plot
import multi_plot

def generate_single_report(arguments):
	env = Environment(
		loader=PackageLoader("cycloanalyzer", "template"),
		autoescape=select_autoescape(["html", "xml"]))
	template = env.get_template("single-report.html")

	activities = parse_activities_csv()
	selected_activity = crunch.select_activity(activities, iso_date=arguments.date)

	arguments.show = False
	single_plot.speed_over_time(arguments)
	single_plot.elevation_over_time(arguments)

	latlong_svg = None
	with open(os.path.join("plot", "latlong.svg"), "r") as latlong_file:
		latlong_svg = latlong_file.read()

	speed_svg = None
	with open(os.path.join("plot", "speed.svg"), "r") as speed_file:
		speed_svg = speed_file.read()

	elevation_svg = None
	with open(os.path.join("plot", "elevation.svg"), "r") as elevation_file:
		elevation_svg = elevation_file.read()

	model = {
		"name": selected_activity.name,
		"date": selected_activity.date,
		"top_speed": selected_activity.max_speed,
		"average_speed": selected_activity.average_speed,
		"elevation_gain": selected_activity.elevation_gain,
		"moving_time": selected_activity.moving_time / 60,
		"distance": selected_activity.distance,
		"average_grade": selected_activity.average_grade,
		"latlong_plot": latlong_svg,
		"speed_plot": speed_svg,
		"elevation_plot": elevation_svg
	}

	pathlib.Path("report").mkdir(exist_ok=True)
	with open(os.path.join("report", "single-report.html"), "w") as report_file:
		report_file.write(template.render(model))


def generate_aggregate_report(arguments):
	env = Environment(
		loader=PackageLoader("cycloanalyzer", "template"),
		autoescape=select_autoescape(["html", "xml"])
	)
	template = env.get_template("multi-report.html")

	rides = parse_activities_csv(type_filter="Ride")
	
	first_datetime = rides[0].date
	last_datetime = rides[-1].date

	weekly_metrics = crunch.crunch_weekly_metrics(rides)
	total_metrics = crunch.crunch_total_metrics(rides)

	arguments.show = False
	multi_plot.average_distance_over_weekday(arguments)
	
	adow_svg = None
	with open(os.path.join("plot", "adow.svg"), "r") as adow_file:
		adow_svg = adow_file.read()
	
	model = {
		"first_datetime": first_datetime,
		"last_datetime": last_datetime,
		"total_ride_count": total_metrics[0],
		"total_ride_time": total_metrics[1],
		"total_ride_distance": total_metrics[2],
		"weekly_ride_average": weekly_metrics[0],
		"weekly_time_average": weekly_metrics[1],
		"weekly_distance_average": weekly_metrics[2],
		"adow_plot": adow_svg
	}

	pathlib.Path("report").mkdir(exist_ok=True)
	with open(os.path.join("report", "multi-report.html"), "w") as report_file:
		report_file.write(template.render(model))
