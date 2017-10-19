#!/bin/bash

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR
. ../../../python_path.sh

# Create the cloudformation json file
python ui_pipeline.py

# Deploy and wait for the stack to build
aws cloudformation update-stack --stack-name ui-pipeline --template-body file://$DIR/ui_pipeline.json --capabilities CAPABILITY_NAMED_IAM
aws cloudformation wait stack-update-complete --stack-name ui-pipeline
