#!/bin/bash

set -e

# Deploy and wait for the stack to build
aws cloudformation delete-stack --stack-name website-cognito-user-pool
aws cloudformation wait stack-delete-complete --stack-name website-cognito-user-pool
