import boto3, json
import time
from datetime import date
from botocore.exceptions import ClientError
import os

def lambda_handler(event, context):
    # Copyright 2022 - Amazon Web Services

    # Permission is hereby granted, free of charge, to any person obtaining a copy of this
    # software and associated documentation files (the "Software"), to deal in the Software
    # without restriction, including without limitation the rights to use, copy, modify,
    # merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
    # permit persons to whom the Software is furnished to do so.

    # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
    # INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
    # PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
    # HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
    # OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
    # SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

    # print('## ENVIRONMENT VARIABLES')
    # print(os.environ)
    # print('## EVENT')
    # print(event)
    response = 'Error remediating the security finding.'
    try:
        # Gather Instance ID from CloudWatch event
        instanceID = event['detail']['resource']['instanceDetails']['instanceId']
        print('## INSTANCE ID: %s' % (instanceID))
        
        # Get instance details
        client = boto3.client('ec2')
        ec2 = boto3.resource('ec2')
        instance = ec2.Instance(instanceID)
        instance_description = client.describe_instances(InstanceIds=[instanceID])
        print('## INSTANCE DESCRIPTION: %s' % (instance_description))

        #-------------------------------------------------------------------
        # Protect instance from termination
        #-------------------------------------------------------------------
        ec2.Instance(instanceID).modify_attribute(
        DisableApiTermination={
            'Value': True
        })
        ec2.Instance(instanceID).modify_attribute(
        InstanceInitiatedShutdownBehavior={
            'Value': 'stop'
        })
        
        #-------------------------------------------------------------------
        # Create tags to avoid accidental deletion of forensics evidence
        #-------------------------------------------------------------------
        ec2.create_tags(Resources=[instanceID], Tags=[{'Key':'status', 'Value':'isolated'}])
        print('## INSTANCE TAGS: %s' % (instance.tags))

        #------------------------------------
        ## Isolate Instance
        #------------------------------------
        print('quarantining instance -- %s, %s' % (instance.id, instance.instance_type))
        
        # Change instance Security Group attribute to terminate connections and allow Forensics Team's access
        instance.modify_attribute(Groups=[os.environ['ForensicsSG']])
        print('Instance ready for root cause analysis -- %s, %s' % (instance.id,  instance.security_groups))

        #------------------------------------
        ## Create snapshots of EBS volumes 
        #------------------------------------
        description= 'Isolated Instance:' + instance.id + ' on account: ' + event['detail']['accountId'] + ' on ' + date.today().strftime("%Y-%m-%d  %H:%M:%S")
        SnapShotDetails = client.create_snapshots(
            Description=description,
            InstanceSpecification = {
                'InstanceId': instanceID,
                'ExcludeBootVolume': False
            }
        )
        print('Snapshot Created -- %s' % (SnapShotDetails))

        response = 'Instance ' + instance.id + ' auto-remediated'        
        
    except ClientError as e:
        print(e)
 
    return response