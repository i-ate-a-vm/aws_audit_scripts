# Import required libraries
import argparse 
import boto3
import pandas
from botocore.exceptions import ClientError, BotoCoreError

# Create required EC2 client to gather VPC data
ec2 = boto3.client('ec2')

# Create argparse object and arguments
parser = argparse.ArgumentParser(description='Check for public S3 buckets in your AWS account.')
parser.add_argument('-v', '--vpc', action='append', help='The single VPC to evaluate. If no VPC is specified, automatically evaluates all VPCs in the account.', required=False)
#parser.add_argument('-r', '--region', action='append', help='The region to evaluate resources for. If no region is specified, automatically uses the region in the specified config.', required=True)

args = parser.parse_args()

# Begin defining functions
def get_vpc():
	# Gathers IDs of all VPCs in the specified region
	# TO DO: Add config detection so -r argument can be made optional 

	# Name tags are optional, so have to use ID. Should still add name to report where they exist
	# When a name doesn't exist, set it equal to None for report
	# Getting tags is proving to be a big pain, so just doing IDs for now
	# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_tags

	# Not seeing a way off the bat to specify region
	vpc = ec2.describe_vpcs()
	# Remove unnecessary keys 
	vpc = vpc['Vpcs']
	vpc_ids = []

	for index, value in enumerate(vpc):
		print(value)
		print(type(value))
		vpc_ids.append(value[index]['VpcId'])

	if args.vpc is None:
		print('No VPC specified; evaluating all VPCs in the current region.')
		print(vpc_ids)
		return vpc_ids

	# If buckets are specified, check that bucket exists and exit if not
	#elif args.vpc:
		# Get string of bucket name specified in cmd line argument
		#bucket_specified = args.bucket[0] # This only works while only one argument is passed in

		#if bucket_specified in vpc_id:
			#return args.bucket
		#elif bucket_specified not in vpc_id:
			#print('ERROR: Specified bucket does not exist in the current AWS account.')
			#exit(1)




def create_vpc_report(results_df):
	# Uses the results_df from !!!!!!!!!!!!!!! function and converts them into the CSV report
	return results_df.to_csv('./output/vpc_audit_data.csv', index=False)

# Main block
get_vpc()