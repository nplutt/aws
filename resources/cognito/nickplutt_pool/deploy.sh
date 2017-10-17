#!/bin/bash

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR
. ../../../python_path.sh

# Create the cloudformation json file
python user_pool.py

# Deploy and wait for the stack to build
aws cloudformation create-stack --stack-name nick-plutt-cognito-user-pool --template-body file://$DIR/user_pool.json
aws cloudformation wait stack-create-complete --stack-name nick-plutt-cognito-user-pool
