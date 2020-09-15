
class Activity:

	def __init__(self):
		self.activity_id = None
		self.date = None
		self.name = None
		self.activity_type = None
		self.elapsed_time = None
		self.distance = None
		self.filename = None
		self.moving_time = None
		self.max_speed = None
		self.average_speed = None
		self.elevation_gain = None
		self.elevation_low = None
		self.elevation_high = None
		self.max_grade = None
		self.average_grade = None
		self.perceived_exertion = None
		self.perceived_relative_effort = None

def create_activity(activity_record):
	activity = Activity()
	activity.activity_id = activity_record["Activity ID"]
	activity.date = activity_record["Activity Date"]
	activity.name = activity_record["Activity Name"]
	activity.activity_type = activity_record["Activity Type"]
	activity.elapsed_time = activity_record["Elapsed Time"]
	activity.distance = activity_record["Distance"]
	activity.filename = activity_record["Filename"]
	activity.moving_time = activity_record["Moving Time"]
	activity.max_speed = activity_record["Max Speed"]
	activity.average_speed = activity_record["Average Speed"]
	activity.elevation_gain = activity_record["Elevation Gain"]
	activity.elevation_low = activity_record["Elevation Low"]
	activity.elevation_high = activity_record["Elevation High"]
	activity.max_grade = activity_record["Max Grade"]
	activity.average_grade = activity_record["Average Grade"]
	activity.perceived_exertion = activity_record["Perceived Exertion"]
	activity.perceived_relative_effort = activity_record["Perceived Relative Effort"]
	return activity
