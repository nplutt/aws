# Angular 4 Build Pipeline
This example will show you how to build an Angular 4 build pipeline in AWS, make
the application available to users through a static web hosted S3 bucket, and save 
the build artifacts to an S3 bucket.

![Alt text](https://github.com/nplutt/aws/blob/master/examples/angular_pipeline/Angular_pipeline.jpg)

In order to build an Angular 4 application in AWS Codebuild, some things must first be added. 
The first thing that needs to be added is [puppeteer](https://www.npmjs.com/package/puppeteer),
which handles installing the most recent up to date Chromium binary. To install puppeteer run the following
command:
```bash
$ npm install puppeteer --save-dev
```
Once puppeteer is installed the following changes must be made to the `karma.config.js` file so that headless 
Chrome can be run in AWS Codebuild: 

1. Set the CHROME_BIN environment variable, to do this add the below line to to the top of the file
    ```javascript
    process.env.CHROME_BIN = require('puppeteer').executablePath();
    ```
2. Modify the browsers array to include ChromeHeadless and ChromeHeadlessCI

    ```javascript
    browsers: ['Chrome', 'ChromeHeadless', 'ChromeHeadlessCI'],
    ```
3. Add a new custom launcher called ChromeHeadlessCI
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

The next step is to add the following test and build commands to the `package.json` file: 
```javascript
"test:ci": "ng test --browser=ChromeHeadlessCI --code-coverage=true --single-run=true",
"build:ci": "ng build --target=production --environment=prod --deploy-url=domain.com",
```
    
Now that the build commands have been added to the `package.json` file, a `buildspec.yaml` file must be created.
The `buildspec.yaml` file holds all of the build commands that will be run during the build process. The below file 
is an example of a build that works for this example.
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
    
Now that the Angular application has been modified to run in AWS Codebuild we must now create the AWS infrastructure
needed for this example. The resources that need to be created are a S3 bucket for hosting the Angular application,
an S3 bucket for holding build artifacts, and a Codebuild build.

Static Web Hosting S3 Bucket Cloudformation Template
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

Artifacts S3 Bucket Cloudformation Template
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

Codebuild Cloudformation Template
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