# Import required libraries
import argparse 
import boto3
import pandas

# Create argparse object and arguments
parser = argparse.ArgumentParser(description='Check for public S3 buckets in your AWS account.')
parser.add_argument('-r', '--region', action='store', type=str, help='The region to evaluate VPC resources for.', required=True)
parser.add_argument('-v', '--vpc', action='append', help='The ID of the single VPC to evaluate. DOES NOT CURRENTLY SUPPORT USING VPC NAME. If no VPC is specified, automatically evaluates all VPCs in the account.', required=False)

args = parser.parse_args()

# Create required EC2 client to gather VPC data, specifying region
region = args.region
ec2 = boto3.client('ec2', region_name=region)

# Begin defining functions
def get_vpcs(): # No changes required
	# Gathers IDs of all VPCs in the specified region
	vpc = ec2.describe_vpcs() 

	# Remove unnecessary keys 
	vpc = vpc['Vpcs']
	vpc_ids = []

	# Grabs the VPC IDs to be used in next steps
	for value in vpc:
		vpc_ids.append(value['VpcId'])

	# If no VPC is specified in cmd line arguments, evaluate all VPCs in the region
	if args.vpc is None:
		print('No VPC specified; evaluating all VPCs in the current region: ' + region)
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



def populate_subnet_report(vpc_subnet_dict):
	# Perform VPC evaluations and populate them
	columns = ['VPC ID', 'Subnet ID', 'Subnet Assigns Public IP'] # This should eventually include data about routes, NACLs, possibly more
	subnet_df = pandas.DataFrame(columns=list(columns))

	for vpc in vpc_subnet_dict.values():
		for subnet in vpc: 
			auto_public_ip = eval_auto_assign_public_subnets(subnet)
			subnet_id = subnet['SubnetId']
			vpc_id = vpc[0]['VpcId']

			# Create dataframe structures to be converted into CSV
			append_series = pandas.Series([vpc_id, subnet_id, auto_public_ip], index=columns)
			subnet_df = subnet_df.append(append_series, ignore_index=True)

	return subnet_df



def create_vpc_report(results_df):
	# Uses the results_df from function and converts them into the CSV report
	return results_df.to_csv('./output/vpc_audit_data.csv', index=False)



# Main block
vpc_ids = get_vpcs()
vpc_subnet_dict = gather_subnets(vpc_ids) 
results_df = populate_subnet_report(vpc_subnet_dict)
create_vpc_report(results_df)
print('VPC(s) evaluated successfully. Output file is located at ./output/vpc_audit_data.csv.')