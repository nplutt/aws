#!/bin/bash

set -e

. ../../python_path.sh

path=$(pwd)

# Create the cloudformation json file
python vpc.py

#Deploy and wait for the stack to build
aws cloudformation create-stack --stack-name vpc --template-body file://$path/vpc.json
aws cloudformation wait stack-create-complete --stack-name vpc
