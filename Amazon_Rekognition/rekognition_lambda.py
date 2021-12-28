################################################
# Lambda function to invoke Amazon Rekognition #
# recognize_celebrities based on s3 Put event  #
################################################

# Module required to worked with Lambda env variables
import os

# Module for AWS SDK for Python
import boto3

# Specify the env variable for the dynamoDB bucket name
TABLE_NAME = os.environ['TABLE_NAME']
# Create resource for AWS Services
dynamodb = boto3.resource('dynamodb')
# Creates a Table sub-resource
table = dynamodb.Table('Faces')
# Create resource for source bucket
s3 = boto3.resource('s3')
# Create resource for target service
rekognition = boto3.client('rekognition')

def lambda_handler(event, context):
    # Get object from s3 CW event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    # Creates an Object resource
    obj = s3.Object(bucket, key)
    # Read Object resource into memory to store as variable
    image = obj.get()['Body'].read()
    
    # Invoke Rekcognition service
    print('Recognizing celebrities...')
    response = rekognition.recognize_celebrities(Image={'Bytes': image})
    
    # Empty list to populate with names of celebrities from CW event
    names = []
    
    # Iterate through all names provided in event
    for celebrity in response['CelebrityFaces']:
        name = celebrity['Name']
        print('Name: ' + name)
        names.append(name)
        
    print(names)
    
    print('Saving face data to DynamoDB table:', TABLE_NAME)
    
    response = table.put_item(
        Item={
                'key': key,
                'names': names,
                }
            )
    
    print(response)
