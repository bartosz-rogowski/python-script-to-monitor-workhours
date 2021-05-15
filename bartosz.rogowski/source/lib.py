import pandas as pd
import datetime
import typing
import os
from constants import *

def read_csv_data(path_to_file: str) -> pd.core.frame.DataFrame:
	'''Function reading data from file

	Arguments:
		path_to_file {str} -- path to a csv file

	Returns:
		DataFrame object containing data from the file
	'''
	if path_to_file.split('.')[-1] != 'csv':
		raise Exception(f"{path_to_file} is not a csv file. Please try again with a valid file.")
	return pd.read_csv(path_to_file, encoding='utf-8', sep=';')

def week_number_from_date(string_date: str) -> int:
	'''Function converting string date to number of the week of a year

	Arguments:
		string_date {str} -- date written in format YYYY-MM-DD

	Returns:
		integer representing number of the week of a year
	'''
	try:
		#string to datetime object
		date = datetime.datetime.strptime(string_date, '%Y-%m-%d')
		weekno = date.isocalendar()[1]
	except (ValueError, UnboundLocalError) as e:
		raise e
	return weekno

def create_dates_list(file: pd.core.frame.DataFrame) -> list:
	'''Function getting string dates of when the reader has noted the activity

	Arguments:
		file {pd.core.frame.DataFrame} -- DataFrame object containing all necessary data

	Returns:
		list containing unique (without repetition) work days
	'''
	dates = [] #string list containing unique work dates
	for i in range(len(file)):
		date = file['Date'][i].split(' ')[0]
		if date not in [d[0] for d in dates]:
			dates.append((date, week_number_from_date(date)))
	return dates

def is_date_weekend(string_date: str) -> bool:
	'''Function checking if string date is a weekend date (Saturday or Sunday)

	Arguments:
		string_date {str} -- date written in format YYYY-MM-DD

	Returns:
		bool -- true if date is a weekend day
	'''
	try:
		#string to datetime object
		date = datetime.datetime.strptime(string_date, '%Y-%m-%d')
		dayno = date.isocalendar()[2]
	except (ValueError, UnboundLocalError) as e:
		raise e
	return dayno in [6, 7]

def working_hours_info(file: pd.core.frame.DataFrame, string_date: str) -> typing.Tuple[str, str, bool]:
	'''Function getting data such as start hour, end hour of the work and assessing whether 
	working time is inconclusive (for example if the first activity is not an ENTRY or the last one - an EXIT)

	Arguments:
		file {pd.core.frame.DataFrame} -- DataFrame object containing all necessary data
		string_date {str} -- date written in format YYYY-MM-DD

	Returns:
		typing.Tuple[
			starting {str} -- string containing time marking the beginning of the work,

			ending {str} -- string containing time marking the end of the work, 

			flag {bool} -- true if worktime is inconclusive
		]
	'''
	flag = False
	hours = []
	events = []
	
	for i in range(len(file)):
		if file['Date'][i].split(' ')[0] == string_date:
			hours.append(file['Date'][i].split(' ')[1])
			events.append(file['Event'][i])

	starting = min(hours)
	ending = max(hours)
	#checking whether worktime is inconclusive
	if events[0] != ENTRY or events[-1] != EXIT:
		flag = True

	return starting, ending, flag

def count_workdays_in_weeks(dates: list) -> list:
	'''Function counting how many workdays there are in a single week.

	Arguments:
		dates {list} -- contains string dates written in format YYYY-MM-DD

	Returns:
		list containing lists 
		[number of workdays in a single week, number of weekend workdays in a single week]
	'''
	unique_week_numbers = list(set([d[1] for d in dates if d[1] in d]))
	workdays_in_week = []
	week_numbers_of_dates = [d[1] for d in dates if d[1] in d and not is_date_weekend(d[0])]
	week_numbers_of_dates_that_are_weekend_day = [d[1] for d in dates if d[1] in d and is_date_weekend(d[0])]

	for weekno in unique_week_numbers: 
		workdays_in_week.append(
			[week_numbers_of_dates.count(weekno), 
			week_numbers_of_dates_that_are_weekend_day.count(weekno)]
			)
	return workdays_in_week

def create_worktime_list(file: pd.core.frame.DataFrame, dates: list) -> list:
	'''Function creating list of tuples containing calculated worktime and literal

	if worktime < UNDERTIME_HOURS -> literal = UNDERTIME_LITERAL

	if worktime > OVERTIME_HOURS -> literal = OVERTIME_LITERAL

	if function working_hours_info marks worktime as inconclusive -> literal = INCONCLUSIVE_LITERAL

	NOTE: Additionaly if function is_date_weekend retuns true -> literal += WEEKEND_LITERAL

	Arguments:
		file {pd.core.frame.DataFrame} -- DataFrame object containing all necessary data
		dates {list} -- contains string dates written in format YYYY-MM-DD

	Returns:
		list of tuples: (
			datetime.timedelta -- worktime length,

			string -- literal
			)
	'''
	worktime_list = []
	literal = []
	for date in [d[0] for d in dates]:
		literal = ''
		start, end, flag = working_hours_info(file, date)
		#convertion from string to datetime object
		start = datetime.datetime.strptime(start, '%H:%M:%S')
		end = datetime.datetime.strptime(end, '%H:%M:%S')
		work_hours = end - start
		if flag:
			literal = INCONCLUSIVE_LITERAL
		elif work_hours > datetime.timedelta(hours=OVERTIME_HOURS):
			literal = OVERTIME_LITERAL
		elif work_hours < datetime.timedelta(hours=UNDERTIME_HOURS):
			literal = UNDERTIME_LITERAL
		if is_date_weekend(date):
			literal += WEEKEND_LITERAL
		worktime_list.append((work_hours, literal))
	return worktime_list

def convert_timedelta_to_HHMMSS_string(timedelta_object: datetime.timedelta) -> str:
	'''Function converting timedelta object to string in format HH:MM:SS

	Arguments:
		timedelta_object {datetime.timedelta} -- timedelta containing information about worktime

	Returns:
		str -- worktime length in format HH:MM:SS
	'''
	minutes, seconds = divmod(timedelta_object.seconds, 60)
	hours, minutes = divmod(minutes, 60)
	hours += 24*timedelta_object.days
	return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def perform_analysis(path_to_file: str, result_file_name: str):
	'''Main function performing all analysis of the working hours problem.

	Arguments:
		path_to_file {str} -- location of a file
		result_file_name {str} -- name of result file
	'''
	ans = None #user's answer if they want to overwrite existing file

	file = read_csv_data(path_to_file)
	#checking if file already exists
	if os.path.exists(result_file_name):
		while ans != 'y':
			ans = input(f"{result_file_name} already exists. Do you want to overwrite this file? [y/n]\n")
			if ans == 'n':
				raise Exception("Program stopped by the user.")
	
	#preparing file and all necessary info
	result_file = open(result_file_name, 'w')
	dates = create_dates_list(file)
	work_hours_list = create_worktime_list(file, dates)
	workingdays_in_weeks = count_workdays_in_weeks(dates)

	summaric_time = datetime.timedelta(seconds = 0)
	#actual workdays are those from Monday to Friday + weekend workdays: Saturday, Sunday
	actual_workdays_in_week = workingdays_in_weeks[0][0] + workingdays_in_weeks[0][1]
	#ecpected time equals default worktime lenght times workdays (but only those from Monday to Friday)
	expected_time = datetime.timedelta(hours = DEFAULT_WORKTIME_LENGTH*workingdays_in_weeks[0][0])
	for i in range(len(dates)): 
		summaric_time += work_hours_list[i][0]
		text = f"Day {dates[i][0]} Work {work_hours_list[i][0]} {work_hours_list[i][1]}"
		#in case of last day in a week, summary informations will be created
		if actual_workdays_in_week == 1:
			if work_hours_list[i][1]:
				text += " "
			text += convert_timedelta_to_HHMMSS_string(summaric_time)
			over_under_time = None #variable for statistical info 
			if summaric_time >= expected_time:
				over_under_time = summaric_time - expected_time
				text += " " + convert_timedelta_to_HHMMSS_string(over_under_time)
			else:
				over_under_time = expected_time - summaric_time
				text += " -" + convert_timedelta_to_HHMMSS_string(over_under_time)
			summaric_time = datetime.timedelta(seconds = 0)
			workingdays_in_weeks.pop(0)
			#checking if there's some more elements on the list
			if workingdays_in_weeks:
				actual_workdays_in_week = workingdays_in_weeks[0][0] + workingdays_in_weeks[0][1]
				expected_time = datetime.timedelta(hours = DEFAULT_WORKTIME_LENGTH*workingdays_in_weeks[0][0])
		else:
			actual_workdays_in_week -= 1

		result_file.write(text + "\n")
		
	result_file.close()
	print("Results has been saved to:", result_file.name)