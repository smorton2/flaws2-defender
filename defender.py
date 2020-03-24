#!/usr/bin/env python3

import boto3
import os
import json
import csv
import gzip

# Objective 1: Download CloudTrail logs
# Step1: Setup CLI.

# Define sts client for security.
security_client = boto3.Session(profile_name='security').client('sts')

# Get the security client's caller identity.
print(security_client.get_caller_identity())

# Step2: Download the logs from the flaws2-logs bucket.

# Define the flaws2-logs bucket.
s3_security = boto3.Session(profile_name='security').resource('s3')
# ToDo (smorton): Add logic to list buckets and allow user to choose the bucket to investigate.
flaws2_logs_bucket = s3_security.Bucket('flaws2-logs')

# Function to list files in an s3 bucket


def s3_ls(bucket):
    for bucket_obj in bucket.objects.all():
        print(bucket_obj)


# List files in flaws2-logs
s3_ls(flaws2_logs_bucket)

# Function to download files from an s3 bucket


def s3_sync(bucket, target_directory):
    # ToDo (smorton): Replace hardcoded directory with one generated by the script.
    nested_directory = os.path.join(
        target_directory, 'AWSLogs/653711331788/CloudTrail/us-east-1/2018/11/28/')
    os.makedirs(nested_directory)

    files = set(os.listdir(nested_directory))
    print(nested_directory)

    for obj in bucket.objects.all():
        obj_filename = obj.key
        if obj_filename not in files:
            bucket.download_file(obj_filename, os.path.join(
                target_directory, obj_filename))


# Download the files.
s3_sync(flaws2_logs_bucket, 'test')

# Objective 2: Access the target account.

# Define sts client for target_security and get the target_security caller identity.
target_security_client = boto3.Session(
    profile_name='target_security').client('sts')
print(target_security_client.get_caller_identity())

# Define target_security and list its buckets.
s3_target_security = boto3.Session(
    profile_name='target_security').resource('s3')
s3_client_target_security = boto3.Session(
    profile_name='target_security').client('s3')
print(s3_client_target_security.list_buckets())

# Objective 3: Read Log Data

# Step 1: Function to find all of the files in the directory and add them to a list.
def list_all_files(downloaded_directory):
    file_list = []
    for root, directories, files in os.walk(downloaded_directory):
        for file in files:
            if '.gz' in file:
                file_list.append(os.path.join(root, file))
    return file_list

# Step 2: Functions to write the contents of a file to a tsv file.
def write_tsv_rows(open_mode, tsv_path, gz_path):
    with open(tsv_path, open_mode) as output_file, gzip.open(gz_path, 'rt') as json_file:
        json_dict = json.load(json_file)
        cleaned_dict = json_dict['Records'][0]
        cleaned_dict = json_dict['Records'][0]
        final_dict = {k: cleaned_dict[k] for k in (
            'eventTime', 'sourceIPAddress', 'eventName')}
        identity_dict = {k: cleaned_dict['userIdentity'].get(
            k, None) for k in ('arn', 'accountId', 'type')}
        final_dict.update(identity_dict)
        tsv = csv.DictWriter(output_file, final_dict.keys(), delimiter='\t')
        tsv.writeheader()
        tsv.writerow(final_dict)

def logs_to_tsv(tsv_path, gz_path):
    if os.path.isfile(tsv_path):
        write_tsv_rows('a+', tsv_path, gz_path)
    else:
        write_tsv_rows('w', tsv_path, gz_path)

# Step 3: Combine the two.  Find all of the files in the directory and update the tsv file with those logs.
def write_to_tsv(target_tsv, source_directory):
    files = list_all_files(source_directory)
    for file in files:
        logs_to_tsv(target_tsv, file)

# Create tsv file with the target logs.
write_to_tsv('target_logs.tsv', 'test')
