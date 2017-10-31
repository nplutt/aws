# Angular 4 Build Pipeline
This tutorial details how to build an Angular 4 build pipeline in AWS, deploy
the application so that it is available to users through a S3 bucket configured for static web hosting, 
and save the build artifacts to an S3 bucket.

![Alt text](https://github.com/nplutt/aws/blob/master/examples/angular_pipeline/Angular_pipeline.jpg)

In order to build an Angular 4 application in AWS Codebuild, some things must first be added. 
The first thing that needs to be added is [puppeteer](https://www.npmjs.com/package/puppeteer),
puppeteer handles installing the most recent up to date Chrome binary, which is needed to run unit tests
from headless Chrome in AWS Codebuild. Puppeteer can be installed by running the following command:
```bash
$ npm install puppeteer --save-dev
```
Once puppeteer is installed the following changes must be made to the `karma.config.js` file to allow 
unit tests to be run from headless Chrome in AWS Codebuild: 

1. Set the `CHROME_BIN` environment variable by adding the below line to the top of the file
    ```javascript
    process.env.CHROME_BIN = require('puppeteer').executablePath();
    ```
2. Modify the array of browsers to include ChromeHeadless and ChromeHeadlessCI
    ```javascript
    browsers: ['Chrome', 'ChromeHeadless', 'ChromeHeadlessCI'],
    ```
3. Create a new custom launcher called ChromeHeadlessCI
    ```javascript
     customLaunchers: {
      ChromeHeadlessCI: {
        base: 'ChromeHeadless',
        flags: ['--no-sandbox']
      }
    }
    ```
    
Once the changes to the `karma.config.js` file are complete the file should look something like:
```javascript
process.env.CHROME_BIN = require('puppeteer').executablePath();

module.exports = function (config) {
  config.set({
    basePath: '',
    frameworks: ['jasmine', '@angular/cli'],
    plugins: [
      require('karma-jasmine'),
      require('karma-chrome-launcher'),
      require('karma-jasmine-html-reporter'),
      require('karma-coverage-istanbul-reporter'),
      require('@angular/cli/plugins/karma')
    ],
    client:{
      clearContext: false // leave Jasmine Spec Runner output visible in browser
    },
    coverageIstanbulReporter: {
      reports: [ 'html', 'lcovonly' ],
      fixWebpackSourcePaths: true
    },
    angularCli: {
      environment: 'dev'
    },
    reporters: ['progress', 'kjhtml'],
    port: 9876,
    colors: true,
    logLevel: config.LOG_INFO,
    autoWatch: true,
    browsers: ['Chrome', 'ChromeHeadless', 'ChromeHeadlessCI'],
    singleRun: false,
    customLaunchers: {
      ChromeHeadlessCI: {
        base: 'ChromeHeadless',
        flags: ['--no-sandbox']
      }
    }
  });
};
```

The next step is to add the test and build commands that will be used in AWS Codebuild to the `package.json` file.
```javascript
"test:ci": "ng test --browser=ChromeHeadlessCI --code-coverage=true --single-run=true",
"build:ci": "ng build --target=production --environment=prod --deploy-url=domain.com",
```
    
Now that the build commands have been added to the `package.json` file, a `buildspec.yml` file must be created in the 
root of the Angular project. The `buildspec.yml` file holds all of the build commands that will be run during the 
build process. Below is an example of a `buildspec.yml` for this tutorial.
```yaml
version: 0.2

phases:
    install:
        commands: 
            - virtualenv node
            - . node/bin/activate
            - pip install nodeenv
            - nodeenv -p
    pre_build:
        commands:
            - npm config set user 0
            - npm config set unsafe-perm true
            - npm install -g @angular/cli@1.4.7
            - npm install
    build:
        commands:
            - npm run test:ci
            - npm run build:ci
    post_build:
        commands:
            - pip install awscli
            - aws s3 cp dist s3://$BUCKET/ --recursive
artifacts:
    files:
        - dist/*
```
    
Now that the Angular application has been modified to be built in AWS Codebuild we must now create the AWS infrastructure
needed for this tutorial. The resources that need to be created are an S3 bucket for hosting the Angular application,
an S3 bucket for storing the build artifacts, and a Codebuild build. Below are the cloudformation templates for creating
all of the necessary resources.

##### Static Web Hosting S3 Bucket Cloudformation Template
This template creates an S3 bucket that is accessible to the world and is specially configured for hosting static web
assets. This configuration sets the Angular app's `index.html` file to be the default asset that is returned to users.

```javascript
{
    "AWSTemplateFormatVersion": "2010-09-09",
    "Description": "This cloudformation template creates an s3 bucket for hosting a static website",
    "Resources": {
        "BucketPolicy": {
            "Properties": {
                "Bucket": {
                    "Ref": "websitenamecom"
                },
                "PolicyDocument": {
                    "Statement": [
                        {
                            "Action": [
                                "s3:GetObject"
                            ],
                            "Effect": "Allow",
                            "Principal": "*",
                            "Resource": [
                                "arn:aws:s3:::websitename.com/*"
                            ]
                        }
                    ]
                }
            },
            "Type": "AWS::S3::BucketPolicy"
        },
        "websitenamecom": {
            "Properties": {
                "AccessControl": "PublicRead",
                "BucketName": "websitename.com",
                "VersioningConfiguration": {
                    "Status": "Enabled"
                },
                "WebsiteConfiguration": {
                    "ErrorDocument": "error.html",
                    "IndexDocument": "index.html"
                }
            },
            "Type": "AWS::S3::Bucket"
        }
    }
}
```  

##### Artifacts S3 Bucket Cloudformation Template
This template creates a private S3 bucket for storing the Angular build artifacts.
```javascript
{
    "AWSTemplateFormatVersion": "2010-09-09",
    "Description": "This cloudformation template creates an s3 bucket for build artifacts",
    "Resources": {
        "artifacts": {
            "Properties": {
                "BucketName": "artifacts",
                "VersioningConfiguration": {
                    "Status": "Enabled"
                }
            },
            "Type": "AWS::S3::Bucket"
        }
    }
}
```

##### Codebuild Cloudformation Template
This template creates an IAM role and the Codebuild instance that will be used for this tutorial.
Some of the things that are specially configured to for this tutorial are:
1. Source location: The repository that the build will pull from. For this tutorial the build will reference
my personal website, which is already configured to be built in Codebuild.
2. Image: The Docker container that the Angular app will be built in. For this tutorial the image is a 
modified Ubuntu image that is pre-loaded with some additional libraries to allow headless Chrome to be run in
Codebuild.
3. Environment variable: The bucket name that the website will be hosted in must be exported. 
This environment variable is used in the `buildspec.yml` file that was added to the Angular app.
```javascript
{
    "AWSTemplateFormatVersion": "2010-09-09",
    "Description": "This CloudFormation template creates a build for the apartments main ui.",
    "Resources": {
        "Angular4Build": {
            "Properties": {
                "Artifacts": {
                    "Location": "artifacts",
                    "Name": "Angular4Build",
                    "Packaging": "zip",
                    "Type": "S3"
                },
                "Environment": {
                    "ComputeType": "BUILD_GENERAL1_SMALL",
                    "EnvironmentVariables": [
                        {
                            "Name": "BUCKET",
                            "Value": "websitename.com"
                        }
                    ],
                    "Image": "nplutt/headless-chrome-ubuntu",
                    "Type": "LINUX_CONTAINER"
                },
                "Name": "Angular4Build",
                "ServiceRole": {
                    "Ref": "Angular4BuildRole"
                },
                "Source": {
                    "Location": "https://github.com/nplutt/personal-website.git",
                    "Type": "GITHUB"
                },
                "TimeoutInMinutes": 10
            },
            "Type": "AWS::CodeBuild::Project"
        },
        "Angular4BuildPolicy": {
            "Properties": {
                "PolicyDocument": {
                    "Statement": [
                        {
                            "Action": [
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents"
                            ],
                            "Effect": "Allow",
                            "Resource": [
                                {
                                    "Fn::Join": [
                                        ":",
                                        [
                                            "arn:aws:logs",
                                            {
                                                "Ref": "AWS::Region"
                                            },
                                            {
                                                "Ref": "AWS::AccountId"
                                            },
                                            "log-group:/aws/codebuild/Angular4Build"
                                        ]
                                    ]
                                },
                                {
                                    "Fn::Join": [
                                        ":",
                                        [
                                            "arn:aws:logs",
                                            {
                                                "Ref": "AWS::Region"
                                            },
                                            {
                                                "Ref": "AWS::AccountId"
                                            },
                                            "log-group:/aws/codebuild/Angular4Build",
                                            "*"
                                        ]
                                    ]
                                }
                            ]
                        },
                        {
                            "Action": [
                                "s3:PutObject",
                                "s3:GetObject",
                                "s3:GetObjectVersion"
                            ],
                            "Effect": "Allow",
                            "Resource": [
                                "arn:aws:s3:::artifacts/*",
                                "arn:aws:s3:::websitename.com/*"
                            ]
                        }
                    ],
                    "Version": "2012-10-17"
                },
                "Roles": [
                    {
                        "Ref": "Angular4BuildRole"
                    }
                ]
            },
            "Type": "AWS::IAM::ManagedPolicy"
        },
        "Angular4BuildProfile": {
            "Properties": {
                "Path": "/service-role/",
                "Roles": [
                    {
                        "Ref": "Angular4BuildRole"
                    }
                ]
            },
            "Type": "AWS::IAM::InstanceProfile"
        },
        "Angular4BuildRole": {
            "Properties": {
                "AssumeRolePolicyDocument": {
                    "Statement": [
                        {
                            "Action": [
                                "sts:AssumeRole"
                            ],
                            "Effect": "Allow",
                            "Principal": {
                                "Service": [
                                    "codebuild.amazonaws.com"
                                ]
                            }
                        }
                    ]
                }
            },
            "Type": "AWS::IAM::Role"
        }
    }
}
```