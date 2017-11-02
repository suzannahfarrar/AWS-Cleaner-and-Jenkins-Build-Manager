import os, javaproperties

def get_job_details():
	# job_details = []
	# job_details['job_name'] = os.environ['JOB_NAME']
	# job_details['build_number'] = os.environ['BUILD_NUMBER']
	# job_details['build_url'] = os.environ['BUILD_URL']
	# job_details['git_url'] = os.environ['GIT_URL']
	# job_details['job_url'] = os.environ['JOB_URL']
	# job_details['branch_name'] = os.environ['BRANCH_NAME']
	# job_details['git_branch'] = os.environ['GIT_BRANCH']
	# job_details['jenkins_url'] = os.environ['JENKINS_URL']

	print (" " + os.environ['JOB_NAME'])
	print (" " + os.environ['BUILD_NUMBER'])

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
