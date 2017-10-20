#!/bin/bash

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR
export PYTHONPATH=$PYTHONPATH:$(git rev-parse --show-toplevel)

# Create the cloudformation json file
python bucket.py

# Deploy and wait for the stack to build
aws cloudformation create-stack --stack-name website-name-com-bucket --template-body file://$DIR/bucket.json
aws cloudformation wait stack-create-complete --stack-name website-name-com-bucket
