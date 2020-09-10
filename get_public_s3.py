# TO DO:
# Write pandas table for CSV
# Create variables that can be used for others, or write instructions on how to make this run using your current config

# using ClientError for boto3 errors - https://stackoverflow.com/questions/42975609/how-to-capture-botocores-nosuchkey-exception
import boto3
import json
from botocore.exceptions import ClientError, BotoCoreError

# below line can be used to get public access block of the account, but errors when no configuration is set
#account_s3_public_setting = s3con.get_public_access_block(AccountId='130922966848')

# Create required S3 clients
s3 = boto3.client('s3')


# Begin defining functions
def get_s3_buckets():
	# Define list that will be returned
	bucket_names = []

	# Gather names of all buckets in the account to be used in other functions
	buckets = s3.list_buckets()

	# Remove unnecessary keys from variable
	buckets = buckets['Buckets']

	# Loop through variable and create a list of names only 
	for name in buckets:
		bucket_names.append(name['Name'])

	return bucket_names


def get_block_public_access_rules(bucket):
	# Checks for public access block rules for all discovered buckets
	# Eventually, this should check for which level of public block is enabled
	# If the block ALL public access is enabled, that should be reflected, and perhaps other checks should be skipped

	public_block_results = []


	# Without doing this as try/except, the exception causes the program to crash even though it just means that there's no public block config
	try:
		block = s3.get_public_access_block(Bucket=bucket)
		if block:
			print("Public access is allowed")
			public = True

	except ClientError as pub_error: 
		if pub_error.response['Error']['Code'] == 'NoSuchPublicAccessBlockConfiguration':
			print("No public access block configuration was found")
			public = False

	finally:
		public_block_results = public


	return public_block_results


def get_bucket_policy(bucket):

	try:
		bucket_policy_results = s3.get_bucket_policy_status(Bucket=bucket)
		bucket_policy_results = bucket_policy_results['PolicyStatus']['IsPublic']
	except ClientError as policy_error:
		if policy_error.response['Error']['Code'] == 'NoSuchBucketPolicy':
			bucket_policy_results = False

	return bucket_policy_results


def get_bucket_acl(bucket):
	bucket_acl_results = []

	# bucket variable gets passed in from loop in identify_public_buckets()
	bucket_acl = s3.get_bucket_acl(Bucket=bucket)
	# Remove unnecessary keys from variable
	bucket_acl = bucket_acl['Grants']

	# index allows us to loop through each ACL entry, since each bucket can have more than one
	for index, entry in enumerate(bucket_acl):
		try:
			if bucket_acl[index]['Grantee']['URI'] == 'http://acs.amazonaws.com/groups/global/AllUsers':
				bucket_acl_results = True
		except KeyError:
			bucket_acl_results = False

	return bucket_acl_results



def identify_public_buckets():
	all_buckets = get_s3_buckets()
	public_buckets = []

	for bucket in all_buckets:

		# populate variables needed to do analysis
		public_block = get_block_public_access_rules(bucket)
		bucket_policy = get_bucket_policy(bucket)
		bucket_acl = get_bucket_acl(bucket)

		# Temporary logic tests
		if public_block == True:
			print(bucket + ' could be PUBLIC according to its Block policy')
		elif public_block == False: 
			print(bucket + ' can NOT be public through its Block policy')

		if bucket_policy == True:
			print(bucket + ' is PUBLIC according to its bucket policy')
		elif bucket_policy == False:
			print(bucket + ' is NOT public through its bucket policy')

		if bucket_acl == True:
			print(bucket + ' is PUBLIC according to its ACL entry')
		elif bucket_acl == False: 
			print(bucket + ' is NOT public through its ACL entry')

		# Logic to populate CSV needs to go here


	return public_buckets


# Bucket Name,Public Status,Public Rule
# test-name,Public,ACL
# test2-name,Not Public,N/A

# main block
identify_public_buckets()
