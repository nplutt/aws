#!/bin/bash

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR
export PYTHONPATH=$PYTHONPATH:$(git rev-parse --show-toplevel)

# Create the cloudformation json file
python vpc.py

#Deploy and wait for the stack to build
aws cloudformation create-stack --stack-name vpc --template-body file://$DIR/vpc.json
aws cloudformation wait stack-create-complete --stack-name vpc
