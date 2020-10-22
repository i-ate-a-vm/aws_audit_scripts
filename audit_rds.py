'''
Script currently doesn't like how I'm parsing the JSON in each of the functions, complaining about a string index that must be an integer because the object type comes in as a list

'''


# Import required libraries
import argparse 
import boto3
import pandas

# Create argparse object and arguments
parser = argparse.ArgumentParser(description='Check for RDS configurations in your AWS account. Groups of checks are outlined as arguments; if no group arguments (-b, -m, -s) are added, all checks are run.')
parser.add_argument('-i', '--instance', action='store', help='The friendly name of the single RDS instance to evaluate. If no instance is specified, automatically evaluates all instances in the account.', required=False)
parser.add_argument('-b', '--backups', action='store_true', help='Only run Backup/ Availability checks.', required=False)
parser.add_argument('-s', '--security', action='store_true', help='Only run Security checks.', required=False)
parser.add_argument('-m', '--monitoring', action='store_true', help='Only run Monitoring checks.', required=False)

args = parser.parse_args()

# Create required RDS client
rds = boto3.client('rds')

# Begin defining functions
def get_rds_instances(arg): # arg is passed the --instance argument in main block
	# Gather data about RDS instances
	if arg == None:
		instance_data = rds.describe_db_instances()
	elif arg != None:
		# This method has options to use DB names, instance IDs and ARNs; should support checking any 
		instance_data = rds.describe_db_instances(DBInstanceIdentifier=arg)

	instance_data = instance_data['DBInstances']

	return instance_data



def get_id_data(instance_data): # This is run no matter which args are included
	# Gather identifying data about instances
	

	# Variables to return
	id_data = {'DBInstanceIdentifier': [], 'Engine': [], 'DBInstanceStatus': []}

	# Populate id_data
	for instance in instance_data:
		id_data['DBInstanceIdentifier'].append(instance['DBInstanceIdentifier'])
		id_data['Engine'].append(instance['Engine'])
		id_data['DBInstanceStatus'].append(instance['DBInstanceStatus'])

	return id_data 



def run_backup_availability_checks(instance_data): # -b argument
	# If called, gathers data about backups and availability for the instance(s)
	backup_data = {'BackupRetentionPeriod': [], 'MultiAZ': [], 'ReadReplicaDBInstanceIdentifiers': [], 'DeletionProtection': []}

	# Populate backup_data
	for instance in instance_data:
		backup_data['BackupRetentionPeriod'].append(instance['BackupRetentionPeriod'])
		backup_data['MultiAZ'].append(instance['MultiAZ'])
		backup_data['ReadReplicaDBInstanceIdentifiers'].append(instance['ReadReplicaDBInstanceIdentifiers'])
		backup_data['DeletionProtection'].append(instance['DeletionProtection'])

	return backup_data



def run_security_checks(instance_data): # -s argument
	# If called, gathers data about security for the instance(s)
	security_data = {'PubliclyAccessible' : [], 'StorageEncrypted': [], 'IAMDatabaseAuthenticationEnabled': [], 'AssociatedRoles': [], 'VpcSecurityGroups': []}

	# Populate security data
	for instance in instance_data:
		security_data['PubliclyAccessible'].append(instance['PubliclyAccessible'])
		security_data['StorageEncrypted'].append(instance['StorageEncrypted'])
		security_data['IAMDatabaseAuthenticationEnabled'].append(instance['IAMDatabaseAuthenticationEnabled'])
		security_data['AssociatedRoles'].append(instance['AssociatedRoles'])
		security_data['VpcSecurityGroups'].append(instance['VpcSecurityGroups'])

	return security_data



def run_monitoring_checks(instance_data): # -m argument
	# If called, gathers data about monitoring for the instance(s)
	monitoring_data = {'MonitoringInterval': [], 'PerformanceInsightsEnabled': []}

	for instance in instance_data:
		monitoring_data['MonitoringInterval'].append(instance['MonitoringInterval'])
		monitoring_data['PerformanceInsightsEnabled'].append(instance['PerformanceInsightsEnabled'])

	return monitoring_data



def identify_and_run_checks(instance_data):
	# Determines which checks need to be run, and returns data to be entered into DF
	backup_data = None
	security_data = None
	monitoring_data = None

	if args.backups == False and args.security == False and args.monitoring == False:
		backup_data = run_backup_availability_checks(instance_data)
		security_data = run_security_checks(instance_data)
		monitoring_data = run_monitoring_checks(instance_data)

	if args.backups == True:
		backup_data = run_backup_availability_checks(instance_data)

	if args.security == True:
		security_data = run_security_checks(instance_data)

	if args.monitoring == True:
		monitoring_data = run_monitoring_checks(instance_data)

	return backup_data, security_data, monitoring_data


def create_rds_df(id_data, backup_data, security_data, monitoring_data):
	# Creates dataframe that will be used to generate CSV report 
	default_columns = ['DBInstanceIdentifier', 'Engine', 'DBInstanceStatus']
	backup_columns = ['BackupRetentionPeriod', 'MultiAZ',	'ReadReplicaDBInstanceIdentifiers',	'DeletionProtection']
	security_columns = ['PubliclyAccessible', 'StorageEncrypted', 'IAMDatabaseAuthenticationEnabled', 'AssociatedRoles', 'VpcSecurityGroups']
	monitoring_columns = ['MonitoringInterval', 'PerformanceInsightsEnabled']

	# Append columns based on which checks are run
	if args.backups == False and args.security == False and args.monitoring == False:
		for column in backup_columns:
			default_columns.append(column)
		for column in security_columns:
			default_columns.append(column)
		for column in monitoring_columns:
			default_columns.append(column)

	if args.backups == True:
		for column in backup_columns:
			default_columns.append(column)

	if args.security == True:
		for column in security_columns:
			default_columns.append(column)

	if args.monitoring == True:
		for column in monitoring_columns:
			default_columns.append(column)

	# Create DF
	rds_df = pandas.DataFrame(columns=list(default_columns)) 

	# Add data from id_data
	rds_df['DBInstanceIdentifier'] = id_data['DBInstanceIdentifier']
	rds_df['Engine'] = id_data['Engine']
	rds_df['DBInstanceStatus'] = id_data['DBInstanceStatus']

	# Determine which variables to pack into DF
	if backup_data != None:
		rds_df['BackupRetentionPeriod'] = backup_data['BackupRetentionPeriod']
		rds_df['MultiAZ'] = backup_data['MultiAZ']
		rds_df['ReadReplicaDBInstanceIdentifiers'] = backup_data['ReadReplicaDBInstanceIdentifiers']
		rds_df['DeletionProtection'] = backup_data['DeletionProtection']

	# security data not packing in correctly
	if security_data != None:
		rds_df['PubliclyAccessible'] = security_data['PubliclyAccessible']
		rds_df['StorageEncrypted'] = security_data['StorageEncrypted']
		rds_df['IAMDatabaseAuthenticationEnabled'] = security_data['IAMDatabaseAuthenticationEnabled']
		rds_df['AssociatedRoles'] = security_data['AssociatedRoles']
		rds_df['VpcSecurityGroups'] = security_data['VpcSecurityGroups']

	if monitoring_data != None:
		rds_df['MonitoringInterval'] = monitoring_data['MonitoringInterval']
		rds_df['PerformanceInsightsEnabled'] = monitoring_data['PerformanceInsightsEnabled']

	return rds_df



def create_rds_report(results_df):
	# Uses the results_df from function and converts them into the CSV report
	return results_df.to_csv('./output/rds_audit_data.csv', index=False)



# Main block
instance_data = get_rds_instances(args.instance)
id_data = get_id_data(instance_data)
backup_data, security_data, monitoring_data = identify_and_run_checks(instance_data)
df = create_rds_df(id_data, backup_data, security_data, monitoring_data)
create_rds_report(df)
print("RDS Instance(s) evaluated successfully. Report located in ./output/rds_audit_data.csv.")