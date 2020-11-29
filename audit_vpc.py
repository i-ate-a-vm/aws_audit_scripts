# Import required libraries
import argparse
import pandas
import modules.build_client as bc
from botocore.exceptions import ClientError


# Create argparse object and arguments
parser = argparse.ArgumentParser(description='Check for VPC configurations in your AWS account.')
parser.add_argument('-r', '--region', action='store', type=str, help='The region to evaluate VPC resources for. If not set, uses the default region specified in your profile.', required=False, default=None)
parser.add_argument('-p', '--profile', action='store', help='AWS credential profile to run the script under. Automatically uses "default" if no profile is specified.', required=False, default='default')
parser.add_argument('-v', '--vpc', action='append', help='The ID of the single VPC to evaluate. DOES NOT CURRENTLY SUPPORT USING VPC NAME. If no VPC is specified, automatically evaluates all VPCs in the account.', required=False)

args = parser.parse_args()

# Create required EC2 client to gather VPC data, specifying region
service = 'ec2'
ec2 = bc.build_client(args.profile, service, args.region)

# Begin defining functions
def get_vpcs(): # No changes required
	# Gathers IDs of all VPCs in the specified region
	try:
		vpc = ec2.describe_vpcs()
	except ClientError as pub_error:
		if pub_error.response['Error']['Code'] == 'InvalidClientTokenId':
			print("Error: Invalid Client Token ID. Validate that the token is valid.")
			exit(1)
		elif pub_error.response['Error']['Code'] == 'AccessDenied':
			print("Error: Access Denied. See README.md for IAM permissions required to execute this script.")
			exit(2)

	# Remove unnecessary keys 
	vpc = vpc['Vpcs']
	vpc_ids = []

	# Grabs the VPC IDs to be used in next steps
	for value in vpc:
		vpc_ids.append(value['VpcId'])

	# If no VPC is specified in cmd line arguments, evaluate all VPCs in the region
	if args.vpc is None:
		print('No VPC specified; evaluating all VPCs in the current region.')
		print('Discovered VPCs: ' + str(vpc_ids))
		return vpc_ids

	# If VPC is specified, check that VPC exists and exit if not
	elif args.vpc:
		# Get string of VPC name specified in cmd line argument
		vpc_specified = args.vpc[0] # This only works while only one argument is passed in

		if vpc_specified in vpc_ids:
			return args.vpc

		elif vpc_specified not in vpc_ids:
			print('ERROR: Specified VPC does not exist in the current AWS account or Region.')
			exit(1)



def gather_subnets(vpc_ids):
	# Gather all subnets from specified VPC(s)
	vpc_subnet_dict = {}

	for vpc in vpc_ids:	
		subnets = ec2.describe_subnets(Filters=[
        {
            'Name': 'vpc-id',
            'Values': [
                vpc,
            		],
        		},
    		],
		)
		
		# Remove unnecessary keys 
		subnets = subnets['Subnets']

		# Map subnets discovered for the iterated VPC to vpc_subnet_dict variable
		for dict in subnets:
			vpc_subnet_dict[str(vpc)] = subnets

	return vpc_subnet_dict



def eval_auto_assign_public_subnets(subnet): 
	# Evaluate discovered subnets for auto-assign public IP setting
	# This is currently called through a loop in a later function, meaning we don't need a permanent assignment for this function
	if subnet['MapPublicIpOnLaunch'] == True:
		auto_public_ip = True

	elif subnet['MapPublicIpOnLaunch'] == False:
		auto_public_ip = False

	return auto_public_ip



def eval_flow_logs(vpc):
	# Evaluates current VPC to determine if flow logs are enabled. If logs are enabled, returns their storage location.
	flow_logs = ec2.describe_flow_logs(Filters=[
        {
            'Name': 'resource-id',
            'Values': [
                vpc,
            		],
        		},
    		],
		)

	# Remove unnecessary keys
	flow_logs = flow_logs['FlowLogs']
	
	# If flow log is inactive, flow_logs['FlowLogs'] returns an empty list
	if flow_logs:
		flow_log_active = flow_logs[0]['FlowLogStatus']
		flow_log_dest = flow_logs[0]['LogDestination']
	elif not flow_logs:
		flow_log_active = 'INACTIVE'
		flow_log_dest = 'N/A'

	return flow_log_active, flow_log_dest



def populate_report(vpc_subnet_dict):
	# Perform VPC evaluations and populate them into DF
	columns = ['VPC ID', 'Flow Logs Active', 'Flow Logs Location', 'Subnet ID', 'Subnet Assigns Public IP']
	vpc_df = pandas.DataFrame(columns=list(columns))

	for vpc in vpc_subnet_dict.values():
		# Perform subnet evaluations and populate them into DF
		vpc_id = vpc[0]['VpcId']
		flow_log_active, flow_log_dest = eval_flow_logs(vpc_id)
		
		# Create dataframe VPC line to be converted into CSV
		append_series = pandas.Series([vpc_id, flow_log_active, flow_log_dest, '', ''], index=columns)
		vpc_df = vpc_df.append(append_series, ignore_index=True)


		for subnet in vpc: 
			# Code to evaluate subnet data runs here, then enters data into DF
			auto_public_ip = eval_auto_assign_public_subnets(subnet)
			subnet_id = subnet['SubnetId']

			# Create dataframe subnet line to be converted into CSV
			append_series = pandas.Series(['', '', '', subnet_id, auto_public_ip], index=columns)
			vpc_df = vpc_df.append(append_series, ignore_index=True)

	return vpc_df



def create_vpc_report(results_df):
	# Uses the results_df from function and converts them into the CSV report
	return results_df.to_csv('./output/vpc_audit_data.csv', index=False)



# Main block
vpc_ids = get_vpcs()
vpc_subnet_dict = gather_subnets(vpc_ids) 
results_df = populate_report(vpc_subnet_dict)
create_vpc_report(results_df)
print('VPC(s) evaluated successfully. Output file is located at ./output/vpc_audit_data.csv.')