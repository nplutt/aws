#!/bin/bash

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR
export PYTHONPATH=$PYTHONPATH:$(git rev-parse --show-toplevel)

path=$(pwd)

# Create the cloudformation json file
python user_pool.py

# Deploy and wait for the stack to build
aws cloudformation update-stack --stack-name website-cognito-user-pool --template-body file://$DIR/user_pool.json
aws cloudformation wait stack-update-complete --stack-name website-cognito-user-pool
