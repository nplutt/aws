#!/bin/bash

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR
export PYTHONPATH=$PYTHONPATH:$(git rev-parse --show-toplevel)

# Create the cloudformation json file
PROJECT_NAME=$(python ui_pipeline.py | grep code_build_name | sed 's/code_build_name: //g')

# Deploy and wait for the stack to build
aws cloudformation create-stack --stack-name ui-pipeline --template-body file://$DIR/ui_pipeline.json --capabilities CAPABILITY_NAMED_IAM
aws cloudformation wait stack-create-complete --stack-name ui-pipeline

# Add a webhook to the build
aws codebuild create-webhook --project-name $PROJECT_NAME
