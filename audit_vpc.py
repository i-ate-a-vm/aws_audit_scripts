# Import required libraries
import argparse 
import boto3
import pandas
from botocore.exceptions import ClientError, BotoCoreError

# Create argparse object and arguments
parser = argparse.ArgumentParser(description='Check for public S3 buckets in your AWS account.')
# To do: add support for VPC name
parser.add_argument('-r', '--region', action='store', type=str, help='The region to evaluate VPC resources for.', required=True)
parser.add_argument('-v', '--vpc', action='append', help='The ID of the single VPC to evaluate. DOES NOT CURRENTLY SUPPORT USING VPC NAME. If no VPC is specified, automatically evaluates all VPCs in the account.', required=False)

args = parser.parse_args()

# Create required EC2 client to gather VPC data, specifying region
region = args.region
ec2 = boto3.client('ec2', region_name=region)

# Begin defining functions
def get_vpcs():
	# Gathers IDs of all VPCs in the specified region
	# TO DO: Add config detection so -r argument can be made optional 

	# Name tags are optional, so have to use ID. Should still add name to report where they exist
	# When a name doesn't exist, set it equal to None for report
	# Getting tags is proving to be a big pain, so just doing IDs for now
	# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_tags

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
	# Current code only works correctly if only one VPC is specified; need to count VPCs and associate VPC-to-subnet relationships
	# https://stackoverflow.com/questions/20585920/how-to-add-multiple-values-to-a-dictionary-key-in-python
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
	
	return subnets



def eval_auto_assign_public_subnets(subnet):
	# Evaluate discovered subnets for auto-assign public IP setting
	subnet_id = subnet['SubnetId']

	if subnet['MapPublicIpOnLaunch'] == True:
		auto_public_ip = True

	elif subnet['MapPublicIpOnLaunch'] == False:
		auto_public_ip = False

	return subnet_id, auto_public_ip



def populate_subnet_report(subnets):
	# Perform VPC evaluations and populate them
	columns = ['VPC ID', 'Subnet ID', 'Subnet Assigns Public IP'] # This should eventually include data about routes, NACLs, possibly more
	subnet_df = pandas.DataFrame(columns=list(columns))
	vpc_id = 'Temp Name' # need to associate this from gather_subnets function, could be with dict using list values: {vpc-nnnn, [sub1, sub2, sub3]}

	for subnet in subnets:

		# Poulate variables needed to do analysis
		subnet_id, auto_public_ip = eval_auto_assign_public_subnets(subnet)

		# Create dataframe structures to be converted into CSV
		append_series = pandas.Series([vpc_id, subnet_id, auto_public_ip], index=columns)
		subnet_df = subnet_df.append(append_series, ignore_index=True)

	return subnet_df



def create_vpc_report(results_df):
	# Uses the results_df from function and converts them into the CSV report
	return results_df.to_csv('./output/vpc_audit_data.csv', index=False)

# Main block
vpc_ids = get_vpcs()
subnet_ids = gather_subnets(vpc_ids) # need a way to associate which subnet came from which VPC
results_df = populate_subnet_report(subnet_ids)
create_vpc_report(results_df)
print('VPC(s) evaluated successfully. Output file is located at ./output/vpc_audit_data.csv.')