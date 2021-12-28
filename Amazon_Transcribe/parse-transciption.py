# Module required to work read/write json files
import json
# Module required to worked with Lambda env variables
import os
# Module defines functions and classes which help in opening URLs
import urllib.request

# Module for AWS SDK for Python
import boto3

# Specify the env variable for the s3 bucket name
BUCKET_NAME = os.environ['BUCKET_NAME']

# Create resource + client for AWS Services
s3 = boto3.resource('s3')
transcribe = boto3.client('transcribe')

# Define Lambda function entry point
def lambda_handler(event, context):
    # Parse the name of transcription job from event detail
    job_name = event['detail']['TranscriptionJobName']
    # Pass job_name as **kwarg to get_transcription_job API
    job = transcribe.get_transcription_job(TranscriptionJobName=job_name)
    # Parse job object to get transcription file uri
    uri = job['TranscriptionJob']['Transcript']['TranscriptFileUri']
    print(uri)

    # Use urllib module to make http request to get file contents
    content = urllib.request.urlopen(uri).read().decode('UTF-8')
    
    # Write raw json contents to CloudWatch logs
    print(json.dumps(content))
    
    # Load raw json into varible 'data'
    data = json.loads(content)
    
    # Pull out just the text from the raw json
    text = data['results']['transcripts'][0]['transcript']
    
    # Save text to s3 bucket
    object = s3.Object(BUCKET_NAME, job_name + '-asrOutput.txt')
    # Specify raw text as body
    object.put(Body=text)