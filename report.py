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
import single_plot
import multi_plot

def generate_single_report(arguments):
	env = Environment(
		loader=PackageLoader("cycloanalyzer", "template"),
		autoescape=select_autoescape(["html", "xml"]))
	template = env.get_template("single-report.html")

	arguments.show = False
	single_plot.speed_over_time(arguments)
	single_plot.elevation_over_time(arguments)

	speed_svg = None
	with open(os.path.join("plot", "speed.svg"), "r") as speed_file:
		speed_svg = speed_file.read()

	elevation_svg = None
	with open(os.path.join("plot", "elevation.svg"), "r") as elevation_file:
		elevation_svg = elevation_file.read()

	model = {
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

	arguments.show = False
	multi_plot.average_distance_over_weekday(arguments)
	
	adow_svg = None
	with open(os.path.join("plot", "adow.svg"), "r") as adow_file:
		adow_svg = adow_file.read()
	
	model = {
		"test": "Test",
		"name": adow_svg
	}

	pathlib.Path("report").mkdir(exist_ok=True)
	with open(os.path.join("report", "multi-report.html"), "w") as report_file:
		report_file.write(template.render(model))