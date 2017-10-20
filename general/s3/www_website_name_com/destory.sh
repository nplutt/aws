#!/bin/bash

set -e

# Deploy and wait for the stack to build
aws cloudformation delete-stack --stack-name www-website-name-com-bucket
aws cloudformation wait stack-delete-complete --stack-name www-website-name-com-bucket
