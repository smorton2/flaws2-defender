#!/usr/bin/env python3

import boto3
import os

# Step1: Setup CLI

# Define sts client for security
security_client = boto3.Session(profile_name='security').client('sts')

# Get the security client's caller identity
print(security_client.get_caller_identity())
