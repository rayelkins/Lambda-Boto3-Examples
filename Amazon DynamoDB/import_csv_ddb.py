"""
Purpose

Shows how to use the AWS SDK for Python (Boto3) to write Amazon DynamoDB
data using batch functions.

Boto3 features a `batch_writer` function that handles all of the necessary 
intricacies of the Amazon DynamoDB batch writing API on your behalf. This 
includes buffering, removing duplicates, and retrying unprocessed items.
"""
import csv
import os
import tempfile

import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Movies')
s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Iterate over S3 event Records in source bucket
    for record in event['Records']:
        # Generate the name of source bucket in event record
        source_bucket = record['s3']['bucket']['name']
        # Generate the name of source bucket in event record
        key = record['s3']['object']['key']
        # Create temp directory object to hold output
        with tempfile.TemporaryDirectory() as tmpdir:
            # Path to download source file from source bucket
            file_path = os.path.join(tmpdir, key)
            print('Downloading your csv now...')
            try:
                s3.download_file(source_bucket, key, file_path)
            except ClientError as err:
                print(error)
                print(
                    f"Either file doesn't exist or you don't "
                    f"have access to it.")
            items = read_csv(file_path)
            
            print('Items are being written to DynamoDB table...')
            with table.batch_writer() as batch:
                for item in items:
                    batch.put_item(Item = item)

def read_csv(file):
    items=[]
    with open(file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data = {}
            data['Meta'] = {}
            data['Year'] = int(row['Year'])
            data['Title'] = row['Title'] or None
            data['Meta']['Length'] = int(row['Length'] or 0)
            data['Meta']['Length'] = int(row['Length'] or 0)
            data['Meta']['Subject'] = row['Subject'] or None
            data['Meta']['Actor'] = row['Actor'] or None
            data['Meta']['Actress'] = row['Actress'] or None
            data['Meta']['Director'] = row['Director'] or None
            data['Meta']['Popularity'] = row['Popularity'] or None
            data['Meta']['Awards'] = row['Awards'] == 'Yes'
            data['Meta']['Image'] = row['Image'] or None
            data['Meta'] = {k: v for k,
                            v in data['Meta'].items() if v is not None}
            items.append(data)
    return items