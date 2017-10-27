# AWS

## Prerequisites
- [AWS CLI](http://docs.aws.amazon.com/cli/latest/userguide/installing.html) which is configured to use a default profile 
that has iam admin rights in the AWS account that you will be deploying resources to
- [virtualenvwrapper](http://virtualenvwrapper.readthedocs.io/en/latest/install.html) 

## Quick Start

Setup environment to deploy resources from:
```bash
$ mkvituralenv aws
$ pip install -Ur requirements.txt
```
Deploy first resource (generic s3 bucket):
- Edit `bucket_name` and `resource_name` in `/general/s3/artifacts/config.py` file.
- From root directory of this project:
```bash
$ ./general/s3/artifacts/deploy.sh
```

## Examples
- [Angular Build Pipeline](https://github.com/nplutt/aws/tree/master/examples/angular_pipeline): A Build pipeline that will build and deploy an Angular application and save the build artifacts to S3
    
## Generic AWS Resources
- [AWS Certificate Manager](https://github.com/nplutt/aws/tree/master/general/acm)
- [Cognito Pool](https://github.com/nplutt/aws/tree/master/general/cognito/website_pool)
- [Cloudfront](https://github.com/nplutt/aws/tree/master/general/cloudfront)
- Pipelines
    * [Angular Pipeline](https://github.com/nplutt/aws/tree/master/general/pipelines/angular_pipeline)
- S3
    * [Artifacts Bucket](https://github.com/nplutt/aws/tree/master/general/s3/artifacts)
    * [Website Redirect Bucket](https://github.com/nplutt/aws/tree/master/general/s3/www_website_name_com)
    * [Website Hosting Bucket](https://github.com/nplutt/aws/tree/master/general/s3/website_name_com)
- [VPC](https://github.com/nplutt/aws/tree/master/general/vpc)

Licence
[MIT](https://github.com/nplutt/aws/blob/master/LICENSE)