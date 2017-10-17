#!/bin/bash

set -e

. ../../../python_path.sh

path=$(pwd)

# Create the cloudformation json file
python user_pool.py

# Deploy and wait for the stack to build
aws cloudformation create-stack --stack-name $stack_name --template-body file://$path/user_pool.json
aws cloudformation wait stack-create-complete --stack-name $stack_name
