#!/bin/bash

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR
export PYTHONPATH=$PYTHONPATH:$(git rev-parse --show-toplevel)

# Create the cloudformation json file
python pipeline.py

# Deploy and wait for the stack to build
aws cloudformation update-stack --stack-name angular-pipeline --template-body file://$DIR/pipeline.json --capabilities CAPABILITY_NAMED_IAM
aws cloudformation wait stack-update-complete --stack-name angular-pipeline
