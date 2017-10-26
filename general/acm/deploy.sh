#!/bin/bash

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR
export PYTHONPATH=$PYTHONPATH:$(git rev-parse --show-toplevel)

# Create the cloudformation json file
python certificate.py

# Deploy and wait for the stack to build
aws cloudformation create-stack --stack-name general-com-certificate --template-body file://$DIR/certificate.json --region us-east-1
aws cloudformation wait stack-create-complete --stack-name general-com-certificate --region us-east-1
