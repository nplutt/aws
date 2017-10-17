#!/bin/bash

set -e

. ../../../python_path.sh

path=$(pwd)

# Create the cloudformation json file
python www_nickplutt_bucket.py

#Deploy and wait for the stack to build
aws cloudformation create-stack --stack-name www-nickplutt-com-bucket --template-body file://$path/www_nickplutt_bucket.json
aws cloudformation wait stack-create-complete --stack-name www-nickplutt-com-bucket
