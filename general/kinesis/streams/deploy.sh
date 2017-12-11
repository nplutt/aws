#!/bin/bash

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR
export PYTHONPATH=$PYTHONPATH:$(git rev-parse --show-toplevel)

# Deploy and wait for the stack to build
aws cloudformation create-stack --stack-name kinesis-stream --template-body file://$DIR/stream.json
aws cloudformation wait stack-create-complete --stack-name kinesis-stream