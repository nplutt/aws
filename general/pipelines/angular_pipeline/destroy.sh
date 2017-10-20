#!/bin/bash

set -e

# Deploy and wait for the stack to build
aws cloudformation delete-stack --stack-name angular-pipeline
aws cloudformation wait stack-delete-complete --stack-name angular-pipeline
