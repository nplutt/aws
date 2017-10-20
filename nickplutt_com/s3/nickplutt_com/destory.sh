#!/bin/bash

set -e

# Deploy and wait for the stack to build
aws cloudformation delete-stack --stack-name nickplutt-com-bucket
aws cloudformation wait stack-delete-complete --stack-name nickplutt-com-bucket
