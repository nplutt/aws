#!/bin/bash

set -e

# Deploy and wait for the stack to build
aws cloudformation delete-stack --stack-name ui-pipeline
aws cloudformation wait stack-delete-complete --stack-name ui-pipeline
