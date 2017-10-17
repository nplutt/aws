#!/bin/bash

set -e

. ../../../python_path.sh

path=$(pwd)

# Create the cloudformation json file
python artifacts.py

#Deploy and wait for the stack to build
aws cloudformation create-stack --stack-name build-artifacts --template-body file://$path/artifacts_bucket.json
aws cloudformation wait stack-create-complete --stack-name build-artifacts
