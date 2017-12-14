#!/bin/bash

set -e

# Delete S3 Objects
./delete_all_s3_objects.sh

# Deploy and wait for the stack to build
aws cloudformation delete-stack --stack-name s3-data-processing-example
aws cloudformation wait stack-delete-complete --stack-name s3-data-processing-example
