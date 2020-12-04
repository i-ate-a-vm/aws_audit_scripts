import boto3
from botocore.exceptions import ProfileNotFound, NoCredentialsError, NoRegionError


def build_client(profile, service, region):
    # Builds Boto3 client to connect to AWS based on how profile is set up, and what cmd line arguments are passed
    if region == None:
        try:
            if profile == 'default':
                session = boto3.session.Session(profile_name='default')
                client = session.client(str(service))
                return client
            else:
                session = boto3.session.Session(profile_name=str(profile))
                client = session.client(str(service))
                return client
        except ProfileNotFound:
            print(
                "Error: Profile Not Found. Please check your typing and ensure the profile is located in your ~/.aws folder.")
            exit(1)
        except NoCredentialsError:
            print("Error: Credentials Not Found. Please ensure your ~/.aws/credentials file is set up correctly.")
            exit(2)
        except NoRegionError:
            print("Error: No Region Found. Please ensure the selected (or default) profile has a region specified.")
            exit(3)

    elif region != None:
        try:
            if profile == 'default':
                session = boto3.session.Session(profile_name='default', region_name=region)
                client = session.client(str(service))
                return client
            elif profile is type(str):
                session = boto3.session.Session(profile_name=str(profile), region_name=region)
                client = session.client(str(service))
                return client
        except ProfileNotFound:
            print(
                "Error: Profile Not Found. Please check your typing and ensure the profile is located in your ~/.aws folder.")
            exit(1)
        except NoCredentialsError:
            print("Error: Credentials Not Found. Please ensure your ~/.aws/credentials file is set up correctly.")
            exit(2)
