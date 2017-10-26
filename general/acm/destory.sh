#!/bin/bash

set -e

# Deploy and wait for the stack to build
aws cloudformation delete-stack --stack-name general-com-certificate --region us-east-1
aws cloudformation wait stack-delete-complete --stack-name general-com-certificate --region us-east-1
