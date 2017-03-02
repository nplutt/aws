from awacs.aws import Action, Allow, Statement, Principal, Policy
from awacs.sts import AssumeRole
from troposphere import Template, Ref, codebuild, iam

from ui_integrated_deployment.common import write_json_to_file
from ui_integrated_deployment.properties import (region, account_number, codebuild_bucket_name, lambda_code_build_project_name,
                                                 lambda_code_build_docker_image, lambda_repo_url, lambda_build_role_name,
                                                 lambda_build_instance_profile, lambda_build_policy, lambda_prefix,
                                                 lambda_timeout, lambda_function_name, website_bucket_name, lambda_role_name)


def create_code_build_template(template=None):
    if not template:
        template = Template()
        template.add_description('This CloudFormation template creates a build for an angular2 build.')
        template.add_version('2010-09-09')

    code_build_role = template.add_resource(
        iam.Role(
            lambda_build_role_name,
            AssumeRolePolicyDocument=Policy(
                Statement=[
                    Statement(
                        Action=[AssumeRole],
                        Effect='Allow',
                        Principal=Principal('Service', ['codebuild.amazonaws.com', 's3.amazonaws.com'])
                    )
                ]
            )
        )
    )

    code_build_instance_profile = template.add_resource(
        iam.InstanceProfile(
            lambda_build_instance_profile,
            Path='/service-role/',
            Roles=[Ref(code_build_role)]
        )
    )

    code_build_role_policies = template.add_resource(
        iam.ManagedPolicy(
            lambda_build_policy,
            PolicyDocument=Policy(
                Version='2012-10-17',
                Statement=[
                    Statement(
                        Effect=Allow,
                        Resource=[
                            'arn:aws:logs:' + region + ':' + account_number + ':log-group:/aws/codebuild/' + lambda_code_build_project_name,
                            'arn:aws:logs:' + region + ':' + account_number + ':log-group:/aws/codebuild/' + lambda_code_build_project_name + ':*',
                        ],
                        Action=[
                            Action('logs', 'CreateLogGroup'),
                            Action('logs', 'CreateLogStream'),
                            Action('logs', 'PutLogEvents')
                        ]
                    ),
                    Statement(
                        Effect=Allow,
                        Resource=[
                            'arn:aws:s3:::*'
                        ],
                        Action=[
                            Action('s3', '*')
                        ]
                    ),
                    Statement(
                        Effect=Allow,
                        Resource=[
                            'arn:aws:iam::' + account_number + ':role/*'
                        ],
                        Action=[
                            Action('iam', 'PassRole'),
                            Action('iam', 'CreateRole'),
                            Action('iam', 'PutRolePolicy'),
                            Action('iam', 'ListRolePolicies'),
                            Action('iam', 'DeleteRolePolicy'),
                            Action('iam', 'DeleteRole'),
                            Action('iam', 'GetRole')
                        ]
                    ),
                    Statement(
                        Effect=Allow,
                        Resource=[
                            'arn:aws:lambda:' + region + ':' + account_number + ':function:' + lambda_function_name
                        ],
                        Action=[
                            Action('lambda', 'CreateFunction'),
                            Action('Lambda', 'UpdateAlias'),
                            Action('Lambda', 'CreateAlias'),
                            Action('Lambda', 'GetFunctionConfiguration'),
                            Action('Lambda', 'AddPermission'),
                            Action('Lambda', 'DeleteFunction')
                        ]
                    )
                ]
            ),
            Roles=[Ref(code_build_role)]
        )
    )

    artifacts = codebuild.Artifacts(
        Type='S3',
        Name=lambda_code_build_project_name,
        Location=codebuild_bucket_name
    )

    environment = codebuild.Environment(
        ComputeType='BUILD_GENERAL1_SMALL',
        Image=lambda_code_build_docker_image,
        Type='LINUX_CONTAINER',
        EnvironmentVariables=[
            codebuild.EnvironmentVariable(Name='REGION', Value=region),
            codebuild.EnvironmentVariable(Name='TIMEOUT', Value=lambda_timeout),
            codebuild.EnvironmentVariable(Name='BUCKET', Value=codebuild_bucket_name),
            codebuild.EnvironmentVariable(Name='PREFIX', Value=lambda_prefix),
            codebuild.EnvironmentVariable(Name='WEB_BUCKET', Value=website_bucket_name),
            codebuild.EnvironmentVariable(Name='LAMBDA_ROLE', Value=lambda_role_name)
        ]
    )

    source = codebuild.Source(
        Location=lambda_repo_url,
        Type='GITHUB'
    )

    project = codebuild.Project(
        lambda_code_build_project_name,
        Artifacts=artifacts,
        Environment=environment,
        Name=lambda_code_build_project_name,
        ServiceRole=Ref(code_build_role),
        TimeoutInMinutes=5,
        Source=source
    )
    code_build = template.add_resource(project)

    write_json_to_file('code_build_template.json', template)

    return template


if __name__ == '__main__':
    create_code_build_template()
