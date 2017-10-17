# UI Deployment Pipeline

This project is a collection of cloud formation scripts that create a ui deployment pipeline, which is documented in the picture below.
![Alt text](./diagram.png?raw=true "")

#### Prerequisites

1. aws cli
2. Linux environment 

#### Setup
In order to run and work on the project, the following commands must be run.

1. `mkvirtualenv ui_depolyment_pipeline`
2. `python setup.py develop`
3. `pip install -r requirements.txt`

#### Deployment
In order to deploy the pipeline, the following properties must be modified in the __properties.py__ file.

* region: This is the aws region that your pipeline will be deloyed in.
* account_number: The account number of the AWS accound that will be deploying the pipeline.
* github_oauth_token: A Github oauth token that will be used to create a hook into your repo.
* codebuild_bucket_name: The name of the s3 bucket that will store your deployment and build artifacts.
* website_bucket_name: The name of the s3 bucket that will hold your website files.
* ui_repo_url: This is an __optional__ property that can be changed. Take note however that this pipeline is made for projects that use the angular2 cli. If you try to use this pipeline for a project that doesn't use the angular2 cli, other changes will have to be made.

Once the __properties.py__ file has been modifed, deploying the build pipeline should be as simple as opening up a bash window and running the command `./deploy.sh`.
