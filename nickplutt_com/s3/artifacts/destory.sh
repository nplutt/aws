#!/bin/bash

set -e

# Deploy and wait for the stack to build
aws cloudformation delete-stack --stack-name nickplutt-build-artifacts
aws cloudformation wait stack-delete-complete --stack-name nickplutt-build-artifacts
