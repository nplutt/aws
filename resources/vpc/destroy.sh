#!/bin/bash

set -e

. ../../python_path.sh

path=$(pwd)

# Create the cloudformation json file
python vpc.py

#Deploy and wait for the stack to build
aws cloudformation delete-stack --stack-name vpc
aws cloudformation wait stack-delete-complete --stack-name vpc
