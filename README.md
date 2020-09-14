# aws_audit_scripts
Scripts to help with auditing your AWS environment.

## Initial Configuration
Many of these scripts assume that you already have working access keys configured to your AWS account. You can find details on how to configure your access keys for CLI use here: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html

## Individual Scripts

### get_public_s3.py
This script checks all of the S3 buckets in the account your access keys are configured to access. It validates:
- Whether any Public Access Block settings are configured to prevent public access for buckets
- Whether any bucket ACLs are allowing public access to the bucket
- Whether any bucket policies are allowing public access to the bucket

Once the validation is complete, a CSV file is created in the `output` folder that outlines where public access was discovered across the account's buckets.

Currently, the script only checks S3 buckets of one account. All S3 buckets of the account are checked.

The script assumes that your configured IAM user has the correct IAM permissions to access S3 bucket permissions. The required actions are listed below, and a full list of actions can be found here: https://docs.aws.amazon.com/IAM/latest/UserGuide/list_amazons3.html

Required actions/ permissions:
GetBucketAcl
GetBucketPolicyStatus
GetBucketPublicAccessBlock
HeadBucket

#### Usage
This script will be more CLI-friendly in the near future. For now, your best bet is to execute `python get_public_s3.py` from the cloned directory. 

#### To Do's
- Add arguments to support matching bucket tags
- Add error checking for invalid IAM permissions for the configured user access key
- Evaluate ACLs of individual objects/ object versions
- Enable passing in more than one bucket to the -b argument
