#!/bin/bash

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR
export PYTHONPATH=$PYTHONPATH:$(git rev-parse --show-toplevel)

# Create the cloudformation json file
python artifacts.py

# Deploy and wait for the stack to build
aws cloudformation create-stack --stack-name nplutt-online-python-artifacts --template-body file://$DIR/artifacts_bucket.json
aws cloudformation wait stack-create-complete --stack-name nplutt-online-python-artifacts
