'''
Imports the tempfile module for temporary space
for generating thumbnail image.
'''

import os
# Imports the operating system module for access to env variables
import tempfile

# Imports the AWS Python SDK module
import boto3
# Imports the Image module from the Pillow package to access
# function for resizing the image
from PIL import Image

s3 = boto3.client('s3')
DEST_BUCKET = os.environ['DEST_BUCKET']
SIZE = 128, 128


def lambda_handler(event, context):
# Iterate over S3 event Records in source bucket
    for record in event['Records']:
# Generate the name of source bucket in event record
        source_bucket = record['s3']['bucket']['name']
# Generate the name of source bucket in event record
        key = record['s3']['object']['key']
# Prefix thumbnail generated from source
        thumb = 'thumb-' + key
# Create temp directory object to hold output before put to dest bucket
        with tempfile.TemporaryDirectory() as tmpdir:
# Path to download source image from source bucket
            download_path = os.path.join(tmpdir, key)
            upload_path = os.path.join(tmpdir, thumb)
            s3.download_file(source_bucket, key, download_path)
            generate_thumbnail(download_path, upload_path)
            s3.upload_file(upload_path, DEST_BUCKET, thumb)

        print('Thumbnail image saved at {}/{}'.format(DEST_BUCKET, thumb))


def generate_thumbnail(source_path, dest_path):
# Log message
    print('Generating thumbnail from:', source_path)
# Create context to open image from source bucket as an image
    with Image.open(source_path) as image:
# This method modifies the image to contain a thumbnail version of 
# itself, no larger than the given size.
        image.thumbnail(SIZE)
        image.save(dest_path)
