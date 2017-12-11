#!/bin/bash

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR
export PYTHONPATH=$PYTHONPATH:$(git rev-parse --show-toplevel)

# Create the cloudformation json file
python stack.py

# Deploy and wait for the stack to build
aws cloudformation create-stack --stack-name s3-data-processing-example --template-body file://$DIR/stack.json --capabilities CAPABILITY_NAMED_IAM
aws cloudformation wait stack-create-complete --stack-name s3-data-processing-example
