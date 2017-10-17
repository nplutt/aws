#!/bin/bash

set -e

# Deploy and wait for the stack to build
aws cloudformation delete-stack --stack-name build-artifacts
aws cloudformation wait stack-delete-complete --stack-name build-artifacts
