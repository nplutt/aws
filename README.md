# AWS

### Prerequisites
- [AWS CLI](http://docs.aws.amazon.com/cli/latest/userguide/installing.html)
    * The AWS CLI should be configured to use a default profile that has iam admin rights in AWS
- [virtualenvwrapper](http://virtualenvwrapper.readthedocs.io/en/latest/install.html) 

### Quick Start

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

### Examples:
- [Angular Build Pipeline](https://github.com/nplutt/aws/tree/master/examples/angular_pipeline)
    * Build pipeline that will build and deploy an Angular application and save the build artifacts to S3
    
### Generic Resources:
- [AWS Certificate Manager](https://github.com/nplutt/aws/tree/master/general/acm)