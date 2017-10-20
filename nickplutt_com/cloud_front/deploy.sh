#!/bin/bash

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR
export PYTHONPATH=$PYTHONPATH:$(git rev-parse --show-toplevel)
export CERT_ARN=$(aws acm list-certificates --region us-east-1 --query 'CertificateSummaryList[?DomainName==`nickplutt.com`]' | jq .[0].CertificateArn |  tr -d '"')

# Create the cloudformation json file
python distribution.py

# Deploy and wait for the stack to build
aws cloudformation create-stack --stack-name nickplutt-cloudfront --template-body file://$DIR/distribution.json
aws cloudformation wait stack-create-complete --stack-name nickplutt-cloudfront
