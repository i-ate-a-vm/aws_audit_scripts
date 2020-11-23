import boto3

def build_client(profile, service, region):
    # Builds Boto3 client to connect to AWS based on how profile is set up, and what cmd line arguments are passed
    if region == None:
        if profile == 'default':
            session = boto3.session.Session(profile_name='default')
            client = session.client(str(service))
        else:
            session = boto3.session.Session(profile_name=str(profile))
            client = session.client(str(service))

    elif region != None:
        if profile == 'default':
            session = boto3.session.Session(profile_name='default',region_name=region)
            client = session.client(str(service))
        else:
            session = boto3.session.Session(profile_name=str(profile),region_name=region)
            client = session.client(str(service))

    return client