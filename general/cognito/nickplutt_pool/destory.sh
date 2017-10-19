#!/bin/bash

set -e

# Deploy and wait for the stack to build
aws cloudformation delete-stack --stack-name nick-plutt-cognito-user-pool
aws cloudformation wait stack-delete-complete --stack-name nick-plutt-cognito-user-pool
