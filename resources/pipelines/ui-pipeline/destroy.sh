#!/bin/bash

set -e

. ../../python_path.sh

path=$(pwd)

# Create the cloudformation json file
python ui_pipeline.py

# Deploy and wait for the stack to build
aws cloudformation delete-stack --stack-name ui-pipeline
aws cloudformation wait stack-delete-complete --stack-name ui-pipeline
