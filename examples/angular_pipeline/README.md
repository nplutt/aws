# Creating an Angular 4 Build Pipeline in AWS
This tutorial details how to create an Angular 4 build pipeline in AWS, deploy
the application so that it is available to users through a S3 bucket configured for static web hosting, 
and save the build artifacts to an S3 bucket. The two parts to this tutorial are, modifying the 
Angular application that will be built so that it can be built in Codebuild, and creating 
the necessary infrastructure in AWS.

![Alt text](https://github.com/nplutt/aws/blob/master/examples/angular_pipeline/Angular_pipeline.jpg)

### Modifying the Angular Application
In order to build the Angular application in Codebuild, headless Chrome must be available so that the
unit tests can be run. In order to do this [puppeteer](https://www.npmjs.com/package/puppeteer) will be 
utilized, puppeteer is an npm package that installs a Chrome binary that can then be used to run unit 
tests. Puppeteer can be installed by running the following command:
```bash
$ npm install puppeteer --save-dev
```
Now that puppeteer has been installed, the `karma.config.js` file must be modified so that the application's
unit tests can be run from headless Chrome. 

1. The `CHROME_BIN` environment variable needs to be set at the top of the `karma.config.js` file
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

Now that the test can be run in headless Chrome the following `test` and `build` commands that will be used in 
Codebuild need to be added to the `package.json` file.
```javascript
"test:ci": "ng test --browser=ChromeHeadlessCI --code-coverage=true --single-run=true",
"build:ci": "ng build --target=production --environment=prod --deploy-url=domain.com",
```
    
Now that there are commands for running the tests and building the application, a `buildspec.yml` file must 
be added to the root of the Angular project. The `buildspec.yml` file holds all of the build commands 
that will be run during the build process. Below is the `buildspec.yml` file that will be used for this 
tutorial.
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

### Creating the AWS Infrastructure  
Now that the Angular application has been modified so that it can be built in Codebuild the AWS infrastructure for 
this tutorial needs to be created. The resources that need to be created are an S3 bucket for hosting the Angular application,
an S3 bucket for storing the build artifacts, and a Codebuild build. Below are the cloudformation templates for creating
all of the necessary resources. Additionally all of the code for creating the resources as well as deployment and 
configuration scripts can be found [here](https://github.com/nplutt/aws/tree/article/examples/angular_pipeline).

#### S3 Bucket Configured for Static Web Hosting Cloudformation Template
Creates an S3 bucket that is accessible to the world and is specially configured for hosting static web assets.
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

#### Artifacts S3 Bucket Cloudformation Template
Creates a private S3 bucket for storing the Angular build artifacts.
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

#### Codebuild Cloudformation Template
Creates an IAM role and the Codebuild build that will be used for building the Angular application.
Some of the things that have been specially configured to for this tutorial are:
1. Source location: The repository that the build will pull from, for this tutorial the build will reference
my personal website which is already configured to be built in Codebuild.
2. Image: The Docker image that the Angular application will be built in, for this tutorial the image is a 
modified Ubuntu image that is pre-loaded with some additional libraries to allow headless Chrome to be run in
it.
3. Environment variable: The bucket name that the website will be hosted in, this environment variable is used
 in the `buildspec.yml` file that was added to the Angular application.
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

Once the Codebuild build has been created a webhook can be added using the AWS CLI.
```bash
$ aws codebuild create-webhook --project-name Angular4Build
```