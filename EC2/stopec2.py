import boto3

def lambda_handler(event, context):
    """This function can stop an ec2 instance on a scheduled basis"""

    # Create ec2 Boto3 client for low-level API mapping
    ec2 = boto3.client('ec2')

    # Generate a list of regions using describe_regions API call
    # Assign regions list to variable 'regions'
    regions = [region['RegionName']
        for region in ec2.client.describe_regions()[Regions]]
   
    # Iterate over each region using ec2 resource
    # Pass in region_name as an identifier
    for region in regions:
        ec2 = boto3.resource('ec2', region_name=region)

        print('Region:', region)

        # Filter for ec2 instances in running state
        # Assign to instances variable
        instances = ec2.instances.filter(
            Filters=[{'Name': 'instance-state-name',
            'Values': ['running']}]
        )

        # Stop running instances
        for instance in instances:
            instance.stop()
            print('Stopped instance: ', instance.id)
