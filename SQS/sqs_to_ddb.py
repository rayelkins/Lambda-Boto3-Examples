# Backport print_function for backwards compatibility
from __future__ import print_function
import logging
# Use built-in package for encoding/decoding JSON data
import json
# Module required to work with Boto3 environment variables
import os
# Module provides classes for manipulating date/time
from datetime import datetime
# AWS Python SDK module
from botocore.exceptions import ClientError
import boto3

# Reference function environment variables
QUEUE_NAME = os.environ['QUEUE_NAME']
MAX_QUEUE_MESSAGES = os.environ['MAX_QUEUE_MESSAGES']
DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']

# Create AWS service resource objects
sqs = boto3.resource('sqs')
dynamodb = boto3.resource('dynamodb')
logger = logging.getLogger(__name__)

# Define function entry point
def lambda_handler(event, context):
    
    # Use service resource to call API to retrieve SQS queue name
    try:
        queue = sqs.get_queue_by_name(QueueName=QUEUE_NAME)
        logger.info("Got queue '%s' with URL=%s", QUEUE_NAME, queue.url)
    except ClientError as error:
        logger.exception("Couldn't get queue named %s.", QUEUE_NAME)
        raise error
    else:
        pass
    
        # Print the number of messages waiting in queue for consumer
        print("ApproximateNumberOfMessages:",
              queue.attributes.get('ApproximateNumberOfMessages'))
        # Iterate through message event records
        for message in event['Records']:
            print("Starting your Lambda Function...")
            body = message["body"]
            id = message['messageId']
            print(str(body))
        
            # Write message to DynamoDB
            table = dynamodb.Table(DYNAMODB_TABLE)
            # Call DDB API to add message item to table variable
            response = table.put_item(
                Item={
                    'MessageId':message['messageId'],
                    'Body':message['body'],
                    'Timestamp':datetime.now().isoformat()
                    },
                )
            print("Wrote message to DynamoDB:", json.dumps(response))
