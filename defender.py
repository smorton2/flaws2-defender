#!/usr/bin/env python3

import boto3
import os

# Step1: Setup CLI.

# Define sts client for security.
security_client = boto3.Session(profile_name='security').client('sts')

# Get the security client's caller identity.
print(security_client.get_caller_identity())

# Step2: Download the logs from the flaws2-logs bucket.

# Define the flaws2-logs bucket.
s3_security = boto3.Session(profile_name='security').resource('s3')
flaws2_logs_bucket = s3_security.Bucket('flaws2-logs')

# Function to list files in an s3 bucket
def s3_ls(bucket):
    for bucket_obj in bucket.objects.all():
        print(bucket_obj)

# List files in flaws2-logs
s3_ls(flaws2_logs_bucket)

# Function to download files from an s3 bucket
def s3_sync(bucket, target_directory):
    nested_directory = os.path.join(target_directory, 'AWSLogs/653711331788/CloudTrail/us-east-1/2018/11/28/') 
    os.makedirs(nested_directory)
    
    files = set(os.listdir(nested_directory))
    print(nested_directory)

s3_sync(flaws2_logs_bucket, 'test')

