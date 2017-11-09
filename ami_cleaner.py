import boto3
import configparser
import sys
import argparse
from datetime import datetime, timedelta

def get_available_images(ec2, tagValue):
	
	filters = [{'Name':'tag:Environment', 'Values':[tagValue]}]

	available_images = ec2.images.filter(Filters=filters).all()
	return available_images

def list_top_resources(items, tagValue, d, ec, ec2, ownerID):
	print ("\nListing resources....")
	if tagValue.lower() == 'dev':
		if  d == "identity":
			print ("\nBuild Server (dcs-identity-api)")
		else:
			print ("\nBuild Server (dcs-profile-api)")
	else:
		if  d == "identity":
			print ("\nMaster Server (dcs-identity-api): ")
		else:
			print ("\nMaster Server (dcs-profile-api): ")

	# Displaying AMIs and Instances
	print ("\n S.No \t AMI ID \t AMI Creation Date \tInstance ID \t\t State \t\t Snapshot ID")
	print("\n")

	instances_r = []
	counter = 0
	extra_instance_counter = 0
	for key, value in items:
		if counter < 5:
			snapshots = get_available_snapshots(ec, ownerID)
			for snapshot in snapshots:
				if snapshot['Description'].find(key) > 0:
					resp = ec.describe_instances()
					for instances1 in resp['Reservations']:
						for instance1 in instances1['Instances']:
							if instance1['ImageId'] == key:
								print (" ",(counter+1),".\t " + key + "\t" , value, "\t"+ instance1['InstanceId'] + "\t" + instance1['State']['Name'] + "\t\tNo Snapshots")
								counter = counter + 1
							if snapshot['Description'].find(instance1['InstanceId']) > 0:
								print (" ",(counter+1),".\t " + key + "\t" , value, "\t"+instance1['InstanceId'] + "\t" + instance1['State']['Name'] + "\t\t" + snapshot['SnapshotId'] )
		counter = counter + 1


def get_available_instances(ec2):
		return ec2.instances.all()

def get_available_snapshots(ec, ownerID):
	snapshots = ec.describe_snapshots(OwnerIds = [ownerID])['Snapshots']
	return snapshots

def get_ami(ec, ec2, no_of_ami, tagValue, ownerID):

	# Getting available AMIs
	ami_images = get_available_images(ec2, tagValue)
	
	ami_identity_dates = {}
	ami_profile_dates = {}

	for image in ami_images:
		for tag in image.tags:
			if tag['Key'] == 'Name':
				created_date = datetime.strptime(
					image.creation_date, "%Y-%m-%dT%H:%M:%S.000Z")
			if tag['Value'].startswith('AMI-dcs-identity-api'):
				ami_identity_dates[image.id] = created_date
			if tag['Value'].startswith('AMI-dcs-profile-api'):
				ami_profile_dates[image.id] = created_date

	items = [(v, k) for k, v in ami_identity_dates.items()]
	items.sort()
	items.reverse()
	items = [(k, v) for v, k in items]

	if len(items) > 0:
		list_top_resources(items, tagValue, "identity", ec, ec2, ownerID)
		delete_ami(ami_images,items, no_of_ami, ec, ec2, ownerID, tagValue, "identity")
	else:
		if tagValue.lower() == 'dev':
			print ("\nNo resources allocated for Build server (dcs-identity-api)")
		else:
			print ("\nNo resources allocated for Master server (dcs-identity-api)")

	items = [(v, k) for k, v in ami_profile_dates.items()]
	items.sort()
	items.reverse()
	items = [(k, v) for v, k in items]
	if len(items) > 0: 
		list_top_resources(items, tagValue, "profile", ec, ec2, ownerID)
		delete_ami(ami_images,items, no_of_ami, ec, ec2, ownerID, tagValue, "profile")
	else:
		if tagValue.lower() == 'dev':
			print ("\nNo resources allocated for Build server (dcs-profile-api)")
		else:
			print ("\nNo resources allocated for Master server (dcs-profile-api)")

def delete_ami(ami_images, items, no_of_ami, ec, ec2, ownerID, tagValue, d):

	print("\n")
	if tagValue.lower() == 'dev':
		if  d == "identity":
			print ("Deleting Resources for Build Server (dcs-identity-api)... ")
		else:
			print ("Deleting Resources for Build Server (dcs-profile-api)... ")
	else:
		if  d == "identity":
			print ("Deleting Resources for Master Server (dcs-identity-api)... ")
		else:
			print ("Deleting Resources for Master Server (dcs-profile-api)... ")

	j = 0
	reserved_ami = []
	reserved_instances = []

	# Storing top 3 image IDs
	for key,value in items:
		if j < int(no_of_ami):
			reserved_ami.append(key)
		j = j + 1

	# Getting top 3 instances connected to the top 3 images for later use
	for ami in reserved_ami:
			snapshots = get_available_snapshots(ec, ownerID)
			for snapshot in snapshots:
				if snapshot['Description'].find(ami) > 0:
					instances = get_available_instances(ec2)
					for instance in instances:
						if snapshot['Description'].find(instance.id) > 0:
							reserved_instances.append(instance.id)

	i = 0
	for key, value in items:

		if i >= int(no_of_ami):
			# Getting all available snapshots connected to AMI
			snapshots = get_available_snapshots(ec, ownerID)
			for snapshot in snapshots:

				if snapshot['Description'].find(key) > 0:
					for image in ami_images:
						if image.id == key:
							# Deregistering the AMI
							# image.deregister()
							print("AMI Deleted - " +key)
					# Checking for all instances connected to AMI
					resp = ec.describe_instances()
					for instances1 in resp['Reservations']:
						for instance1 in instances1['Instances']:
							s_instances = set(reserved_instances)
							if instance1['ImageId'] == key:
								if not instance1['InstanceId'] in s_instances:
							 		# Terminating connected instance
									# instance.terminate()
									print ("Instance (" + instance1['InstanceId']+ ") - Terminated")
								else:
									if instance1['State']['Name'] == 'running':
										print("Instance ("+instance1['InstanceId']+") - Not terminated (In use by one of top "+no_of_ami+" AMIs)")
									else:
										# Terminating connected instance
										# instance.terminate()
										print ("Instance (" + instance1['InstanceId'] + ") - Terminated (In use by one of top "+no_of_ami+" AMIs but stopped)")
							if snapshot['Description'].find(instance1['InstanceId']) > 0 :
								# Checking if the instances we are going to terminate are being used by the top AMIs in use
								if not instance1['InstanceId'] in s_instances: 
									# Terminating connected instance
									# instance.terminate()
									print ("Instance (" + instance1['InstanceId'] + ") - Terminated")
								else:
									if instance1['State']['Name'] == 'running':
										print("Instance ("+instance1['InstanceId']+") - Not terminated (In use by one of top "+no_of_ami+" AMIs)")
									else:
										# Terminating connected instance
										# instance.terminate()
										print ("Instance (" + instance1['InstanceId'] + ") - Terminated (In use by one of top "+no_of_ami+" AMIs but stopped)")
					# Deleting associated snapshot
					# snap = ec.delete_snapshot(SnapshotId=snapshot['SnapshotId'])
					print("Snapshot (" + snapshot['SnapshotId'] + ") - Deleted")
					print("\n-")
		i = i + 1
	if i > int (no_of_ami) :
		print ("Count of deleted AMIs: " , (i - int(no_of_ami)))
	else: 
		print ("Count of deleted AMIs: 0")
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('no_of_ami', help='Number of AMIs to save')
    parser.add_argument('env_name', help= 'Environment value to filter AMIs')
    args = parser.parse_args()
    no_of_ami = args.no_of_ami
    env_name = args.env_name

    # Getting config information
    region = ['us-east-2','us-east-1','us-west-1','us-west-2','ca-central-1','ap-south-1','ap-northeast-2','ap-southeast-1','ap-southeast-2','ap-northeast-1','eu-central-1','eu-west-1','eu-west-2','sa-east-1']
    ec = boto3.client('ec2', region_name='ap-south-1')
    ec2 = boto3.resource('ec2', region_name='ap-south-1')
    ownerID = boto3.client('sts').get_caller_identity()['Account']
    
    get_ami(ec, ec2, no_of_ami, env_name, ownerID)

if  __name__ =='__main__':main()