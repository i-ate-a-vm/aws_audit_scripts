# Import required libraries
import boto3
import pandas
from botocore.exceptions import ClientError, BotoCoreError

# Create required S3 clients
s3 = boto3.client('s3')

# Begin defining functions
def get_s3_buckets():
	# Gathers names of all S3 buckets in the account which access keys are configured for

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

	public_block_results = []

	try:
		block = s3.get_public_access_block(Bucket=bucket)
		block = block['PublicAccessBlockConfiguration']
		values = block.values()

		# The all() function validates whether all values are True
		if all(values) == True:
			public = True 

		# any() function returns True if any item in an iterable is True
		elif any(result == True for result in values):
			public = "Partially Blocked"

		# When someone manually specifies no public access block, this will catch it and still list it as False
		else:
			public = False

	# Check for non-existent public access block configuration and specify if nothing is set
	except ClientError as pub_error: 
		if pub_error.response['Error']['Code'] == 'NoSuchPublicAccessBlockConfiguration':
			public = "Validate manually - no configuration set"

	finally:
		public_block_results = public

	return public_block_results


def get_bucket_policy(bucket):
	# Checks for bucket policies that make the bucket public

	try:
		bucket_policy_results = s3.get_bucket_policy_status(Bucket=bucket)
		bucket_policy_results = bucket_policy_results['PolicyStatus']['IsPublic']
	
	# Checks for non-existent bucket policy and sets result to False
	except ClientError as policy_error:
		if policy_error.response['Error']['Code'] == 'NoSuchBucketPolicy':
			bucket_policy_results = False

	return bucket_policy_results


def get_bucket_acl(bucket):
	# Checks for bucket ACLs that make the bucket public

	bucket_acl_results = []

	# Bucket variable gets passed in from loop in identify_public_buckets()
	bucket_acl = s3.get_bucket_acl(Bucket=bucket)

	# Remove unnecessary keys from variable
	bucket_acl = bucket_acl['Grants']

	# Index allows us to loop through each ACL entry, since each bucket can have more than one
	for index, entry in enumerate(bucket_acl):
		try:
			if bucket_acl[index]['Grantee']['URI'] == 'http://acs.amazonaws.com/groups/global/AllUsers':
				bucket_acl_results = True
		except KeyError:
			bucket_acl_results = False

	return bucket_acl_results


def identify_public_buckets(all_buckets):
	# Creates dataframe that will be used to generate CSV report and validates which parts of bucket permissions are public, if any
	
	columns = ['Bucket Name', 'Public Block Enabled', 'Bucket Policy Public', 'Bucket ACL Public']
	bucket_df = pandas.DataFrame(columns=list(columns)) # when a DF is created from a list, it puts the values in the first column rather than first row


	for bucket in all_buckets:

		# Populate variables needed to do analysis
		public_block = get_block_public_access_rules(bucket)
		bucket_policy = get_bucket_policy(bucket)
		bucket_acl = get_bucket_acl(bucket)

		# Create dataframe structures to be converted into CSV
		append_series = pandas.Series([bucket, public_block, bucket_policy, bucket_acl], index=columns) # This data is coming in the way I want it to - just not loading into DF correctly
		bucket_df = bucket_df.append(append_series, ignore_index=True)

	return bucket_df


def create_csv(results_df):
	# Uses the results_df from identify_public_buckets function and converts them into the CSV report
	return results_df.to_csv('./output/s3_public_data.csv', index=False)


# Main block
all_buckets = get_s3_buckets()
results_df = identify_public_buckets(all_buckets)
create_csv(results_df)
print('S3 buckets evaluated successfully. Output file is located at ./output/s3_public_data.csv.')