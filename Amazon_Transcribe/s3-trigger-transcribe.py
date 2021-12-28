############################################################
# This functions triggers the Transcribe service start job #
# API after media file is uploaded to S3 source bucket.    #
############################################################

# Import AWS SDK for Python
import boto3

# Create required services clients
s3 = boto3.client('s3')
transcribe = boto3.client('transcribe')

# Create standard lambda entry point
def lambda_handler(event, context):
    # Iterate over S3 event Records in source bucket
    for record in event['Records']:
        # Generate the name of source bucket in event record
        source_bucket = record['s3']['bucket']['name']
        # Generate the name of source bucket in event record
        key = record['s3']['object']['key']
        # s3 URI that points to source objects
        object_uri = f"s3://{source_bucket}/{key}"
    
        # Call the starttransciptionjob API
        response = transcribe.start_transcription_job(
            # Create job name as file (key) uploaded
            TranscriptionJobName=key,
            # Specify the file that has been uploaded
            Media={'MediaFileUri': object_uri},
            # Tells service the file format
            MediaFormat='mp3',
            # Tells service which language is used in file
            LanguageCode='en-US',
        )
        # Printed response daved to Cloudwatch logs
        print(response)