#!/bin/bash

set -e

# Deploy and wait for the stack to build
aws cloudformation delete-stack --stack-name nplutt-online-python-artifacts
aws cloudformation wait stack-delete-complete --stack-name nplutt-online-python-artifacts
