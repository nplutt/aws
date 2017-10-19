#!/bin/bash

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR
. ../../../python_path.sh

# Create the cloudformation json file
python nickplutt_bucket.py

# Deploy and wait for the stack to build
aws cloudformation create-stack --stack-name nickplutt-com-bucket --template-body file://$DIR/nickplutt_bucket.json
aws cloudformation wait stack-create-complete --stack-name nickplutt-com-bucket
