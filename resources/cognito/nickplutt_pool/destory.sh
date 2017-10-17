#!/bin/bash

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR
. ../../../python_path.sh

path=$(pwd)

# Create the cloudformation json file
python user_pool.py

# Deploy and wait for the stack to build
aws cloudformation delete-stack --stack-name apartments-cognito-user-pool
aws cloudformation wait stack-delete-complete --stack-name apartments-cognito-user-pool
