#!/bin/bash

set -e

. ../../python_path.sh

path=$(pwd)

# Create the cloudformation json file
python ui_pipeline.py

# Deploy and wait for the stack to build
aws cloudformation create-stack --stack-name ui-pipeline --template-body file://$path/ui_pipeline.json --capabilities CAPABILITY_NAMED_IAM
aws cloudformation wait stack-create-complete --stack-name ui-pipeline
