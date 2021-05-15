from lib import perform_analysis, is_date_weekend
import argparse

description='''This script creates report of worktime based on csv file.
	Possible arguments:
		* path - path to csv file containing data
'''

def parserFunction():
	'''Parser for giving additional argument - path to file
	'''
	parser = argparse.ArgumentParser(description)
	parser.add_argument('-p', '--path', type=str, default='input.csv', help='path to csv file')
	parser.add_argument('-rn', '--result_name', type=str, default='result', help='name of the result file')


	args = parser.parse_args()
	return args

if __name__ == '__main__':
	args = parserFunction()
	try:
		perform_analysis(args.path, args.result_name)
	except Exception as e:
		print(e)