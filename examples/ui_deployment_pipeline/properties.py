# Base
region = ''
account_number = ''
github_oauth_token = ''

# UI Code Build Params
ui_codebuild_project_name = 'angular2build'
ui_codebuild_docker_image = 'nplutt/front-end-build-server:latest'
ui_repo_url = 'https://github.com/nplutt/angular2-seed.git'
ui_build_role_name = 'UICodeBuildRole'
ui_build_instance_profile = 'UICodeBuildProfile'
ui_build_policy = 'UICodeBuildPolicy'

# UI Code Pipeline Params
ui_pipeline_project_name = 'ui'
ui_repo_owner = 'nplutt'
ui_repo_name = 'angular2-seed'
ui_branch = 'master'
ui_pipeline_role_name = 'UIPipelineRole'
ui_pipeline_instance_profile = 'UIPipelineProfile'
ui_pipeline_policy = 'UIPipelinePolicy'

# Lambda Code Build Params
lambda_code_build_project_name = 'lambdas3unzip'
lambda_code_build_docker_image = 'nplutt/front-end-build-server:latest'
lambda_repo_url = 'https://github.com/nplutt/lambda-s3-unzip'
lambda_build_role_name = 'S3UnzipCodeBuildRole'
lambda_build_instance_profile = 'S3UnzipCodeBuildProfile'
lambda_build_policy = 'S3UnzipCodeBuildPolicy'
lambda_timeout = '60'
lambda_prefix = 'ui/MyAppBuild/'
lambda_function_name = 's3-unzip'

# Lambda iam role
lambda_role_name = 'S3UnzipRole'
lambda_policy_name = 'S3UnzipPolicy'
lambda_profile_name = 'S3UnzipProfile'

# S3 Params
codebuild_bucket_name = ''
website_bucket_name = ''
