import os, javaproperties

def get_job_details():
	print (" Job name: " + os.environ['JOB_NAME'])
	print (" Build Number: " + os.environ['BUILD_NUMBER'])

def check_repository():
	
	# Checking input.properties file
	with open('input.properties', 'rb') as f:
		p = javaproperties.load(f)

	print(" Repository URL: " + os.environ['GIT_URL'])

	print(" Branches: " + os.environ['GIT_BRANCH'])
	
	if p['repo_path'] == ("\""+os.environ['GIT_URL']+"\""):
		print(" Repository check: SUCCESS")	
	else:
		print(" Repository check: FAILURE")

def check_munit_report():
	
	f = open('filemunittest.txt', 'r')
	file = f.readlines()
	error_lines = 0
	warning_lines = 0
	printList = []
	for line in file:
		if ('ERROR' in line):
			error_lines = error_lines + 1
		if ('WARNING' in line):
			warning_lines = warning_lines + 1
		if ('ERROR' in line) or ('WARNING' in line):
			printList.append(line)
	for item in printList:
		print (item)

	print(" Total number of errors: ",error_lines)
	print(" Total number of warnings: ", warning_lines)

get_job_details()
check_repository()
check_munit_report()
