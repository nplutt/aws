#!/bin/bash
# This script deploys the ui_integrated_deployment

path=$(pwd)

# Create all of the cloudformation scripts so that properties are all initialized
cd s3 && python create_s3_buckets.py && cd ..
cd lambda_code_build && python lambda_iam_role.py && python create_code_build_template.py && cd ..
cd ui_code_pipeline && python create_code_pipeline_template.py && cd ..

# Deploy s3 buckets
aws cloudformation create-stack --stack-name uis3buckets1 --template-body file://$path/s3/s3_buckets_template.json
aws cloudformation wait stack-create-complete --stack-name uis3buckets1


# Deploy the lambda function
aws cloudformation create-stack --stack-name lambdas3unzipiam1 --template-body file://$path/lambda_code_build/lambda_iam_role.json --capabilities CAPABILITY_NAMED_IAM
aws cloudformation create-stack --stack-name lambdas3unzip1 --template-body file://$path/lambda_code_build/code_build_template.json --capabilities CAPABILITY_NAMED_IAM
aws cloudformation wait stack-create-complete --stack-name lambdas3unzip1
aws codebuild start-build --project-name lambdas3unzip


# Deploy the ui code pipeline
aws cloudformation create-stack --stack-name uipipeline --template-body file://$path/ui_code_pipeline/code_pipeline_template.json --capabilities CAPABILITY_NAMED_IAM
aws cloudformation wait stack-create-complete --stack-name uipipeline
