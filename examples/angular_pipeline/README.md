# Angular 4 Build Pipeline
This example will show you how to build out an Angular 4 build pipeline in AWS, make
the application available to users through a static web hosted S3 bucket, and save 
the build artifacts to an S3 bucket.

![Alt text](https://github.com/nplutt/aws/blob/master/examples/angular_pipeline/Angular_pipeline.jpg)

In order to build our Angular 4 application in AWS Codebuild we must first make some changes 
to the Angular application that we are looking to build. The first thing that needs to be done is 
installing [puppeteer](https://www.npmjs.com/package/puppeteer), which handles installing the 
most recent up to date Chromium binary.
```bash
$ npm install puppeteer --save-dev
```
Once puppeteer is installed the following changes must be made to the `karma.config.js` file. 
* Add this line to the top of the file
    ```javascript
    process.env.CHROME_BIN = require('puppeteer').executablePath();
    ```
* Modify the browsers array to include ChromeHeadless and ChromeHeadlessCI
    ```javascript
    browsers: ['Chrome', 'ChromeHeadless', 'ChromeHeadlessCI'],
    ```
* Add a new custom launcher called ChromeHeadlessCI
    ```javascript
     customLaunchers: {
      ChromeHeadlessCI: {
        base: 'ChromeHeadless',
        flags: ['--no-sandbox']
      }
    }
    ```
    
Once the changes to the `karma.config.js` file are complete the file should look something like this:
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

The next step is to add test and build commands to the `package.json` file. 
* Add test command
    ```javascript
    "test:ci": "ng test --browser=ChromeHeadlessCI --code-coverage=true --single-run=true",
    ```
* Add build command with the domain name that you will be deploying to
    ```javascript
    "build:ci": "ng build --target=production --environment=prod --deploy-url=domain.com",
    ```
    
Now that there are build commands in the `package.json` file a `buildspec.yaml` file must be created.
This file holds all of the build commands that will be run when our build executes.
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
            - npm install @angular/cli@1.4.7
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
    
Now that the application is ready to be build in Codebuild we must now create the S3 buckets
that will hold our deployed code and build artifacts.