# aws_audit_scripts
Scripts to help with auditing your AWS environment.

## Initial Configuration
These scripts assume that you already have working access keys configured to your AWS account. You can find details on how to configure your access keys for CLI use here: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html

While your profile is checked for credentials, you can manually specify the region and named profile to use in each script, ensuring that you can use values outside of your `~/.aws/config` file to run the scripts.

## Individual Scripts

### audit_s3.py
This script checks all of the S3 buckets in the account your access keys are configured to access. It validates:
- Whether any Public Access Block settings are configured to prevent public access for buckets
- Whether any bucket ACLs are allowing public access to the bucket
- Whether any bucket policies are allowing public access to the bucket

Once the validation is complete, a CSV file is created in the `output` folder that outlines where public access was discovered across the account's buckets.

Currently, the script only checks S3 buckets of one account. All S3 buckets of the account are checked unless the `-b` argument is used to specify a bucket. At the moment, only one bucket can be specified.

The script assumes that your configured IAM user has the correct IAM permissions to access S3 buckets. The required actions are listed below, and a full list of actions can be found here: https://docs.aws.amazon.com/IAM/latest/UserGuide/list_amazons3.html

Required actions/ permissions:
GetBucketAcl
GetBucketPolicyStatus
GetBucketPublicAccessBlock
HeadBucket

#### Usage
Execute `python audit_s3.py` from the cloned directory. Adding the `-h` argument will give help details.

### audit_rds.py
This script has multiple sets of checks it can run against RDS instances (Backups, Security, Monitoring). It validates:
- Backup/ availability settings, such as how long backups are retained for and whether read replicas/ mutli-AZ are in use
- Security settings, such as deletion protection, public accessibility, security groups in use, storage encryption, etc.
- Monitoring settings, such as the monitoring interval and performance insights

Once the validation is complete, a CSV file is created in the `output` folder that outlines RDS findings.

Currently, the script only checks RDS instances of one account. All RDS instances of the account are checked unless the `-i` argument is used to specify an instance. At the moment, only one instance can be specified, and the friendly instance name (rather than instance ID) must be used.

The script assumes that your configured IAM user has the correct IAM permissions to access RDS instances. The required actions are listed below, and a full list of actions can be found here: https://docs.aws.amazon.com/IAM/latest/UserGuide/list_amazonrds.html

Required actions/ permissions:
DescribeDBInstances

#### Usage
Execute `python audit_rds.py` from the cloned directory. Adding the `-h` argument will give help details.

### audit_vpc.py
This script validates multiple security settings in your VPCs, including -  
- Whether VPCs are collecting flow logs, and if so, where the flow logs are being output
- Whether subnets automatically assign public IPs to instances launched in them
- More to come (this is admittedly the least useful of the three scripts)

Once the validation is complete, a CSV file is created in the `output` folder that outlines findings.

Currently, the script only checks VPC settings of one account. All VPCs of the account are checked unless the `-v` argument is used to specify a VPC. At the moment, only one VPC can be specified.

The script assumes that your configured IAM user has the correct IAM permissions to access VPC and subnet info. The required actions are listed below, and a full list of actions can be found here: https://docs.aws.amazon.com/IAM/latest/UserGuide/list_amazonec2.html

Required actions/ permissions:
DescribeSubnets
DescribeVpcs

#### Usage
Execute `python audit_vpc.py` from the cloned directory, including required `-r` argument. Adding the `-h` argument will give help details.


#### To Do's
All scripts:
- Add AWS config/ credentials detection
- Add arguments to support matching tags
- Add error checking for invalid IAM permissions for the configured user access key
- Enable passing in more than one argument to argparse

audit_s3.py: 
- Evaluate ACLs of individual objects/ object versions
- Ensure get_bucket_acl function's loop can correctly handle evaluation of more than one ACL result

audit_rds.py:
- Add error checking for making sure specified instance exists (if -i arg is used)
- Add support for checking RDS instance ID or ARN instead of friendly name
- Add more info about available snapshots, logging, etc. 

audit_vpc.py:
- Add support for VPC name instead of ID
- Add more checks, such as checking for VPC flow logs, non-default NACL rules are in place, etc.
