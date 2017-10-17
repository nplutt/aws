#!/bin/bash

set -e

. ../../../python_path.sh

path=$(pwd)

# Create the cloudformation json file
python nickplutt_bucket.py

#Deploy and wait for the stack to build
aws cloudformation create-stack --stack-name nickplutt-com-bucket --template-body file://$path/nickplutt_bucket.json
aws cloudformation wait stack-create-complete --stack-name nickplutt-com-bucket
