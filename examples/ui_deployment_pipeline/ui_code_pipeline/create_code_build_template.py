from awacs.aws import Action, Allow, Statement, Principal, Policy
from awacs.sts import AssumeRole
from troposphere import Template, Ref, codebuild, iam

from ui_integrated_deployment.common import write_json_to_file
from ui_integrated_deployment.properties import (region, account_number, ui_codebuild_project_name, codebuild_bucket_name,
                                                 ui_codebuild_docker_image, ui_repo_url, ui_build_role_name,
                                                 ui_build_instance_profile, ui_build_policy)


def create_code_build_template(template=None):
    if not template:
        template = Template()
        template.add_description('This CloudFormation template creates a build for an angular2 build.')
        template.add_version('2010-09-09')

    code_build_role = template.add_resource(
        iam.Role(
            ui_build_role_name,
            AssumeRolePolicyDocument=Policy(
                Statement=[
                    Statement(
                        Action=[AssumeRole],
                        Effect='Allow',
                        Principal=Principal('Service', ['codebuild.amazonaws.com'])
                    )
                ]
            )
        )
    )

    code_build_instance_profile = template.add_resource(
        iam.InstanceProfile(
            ui_build_instance_profile,
            Path='/service-role/',
            Roles=[Ref(code_build_role)]
        )
    )

    code_build_role_policies = template.add_resource(
        iam.ManagedPolicy(
            ui_build_policy,
            PolicyDocument=Policy(
                Version='2012-10-17',
                Statement=[
                    Statement(
                        Effect=Allow,
                        Resource=[
                            'arn:aws:logs:' + region + ':' + account_number + ':log-group:/aws/codebuild/' + ui_codebuild_project_name,
                            'arn:aws:logs:' + region + ':' + account_number + ':log-group:/aws/codebuild/' + ui_codebuild_project_name + ':*',
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
                            'arn:aws:s3:::' + codebuild_bucket_name + '/*'
                        ],
                        Action=[
                            Action('s3', 'PutObject'),
                            Action('s3', 'GetObject'),
                            Action('s3', 'GetObjectVersion')
                        ]
                    )
                ]
            ),
            Roles=[Ref(code_build_role)]
        )
    )

    artifacts = codebuild.Artifacts(
        Type='S3',
        Name=ui_codebuild_project_name,
        Location=codebuild_bucket_name
    )

    environment = codebuild.Environment(
        ComputeType='BUILD_GENERAL1_SMALL',
        Image=ui_codebuild_docker_image,
        Type='LINUX_CONTAINER'
    )

    source = codebuild.Source(
        Location=ui_repo_url,
        Type='GITHUB'
    )

    project = codebuild.Project(
        ui_codebuild_project_name,
        Artifacts=artifacts,
        Environment=environment,
        Name=ui_codebuild_project_name,
        ServiceRole=Ref(code_build_role),
        TimeoutInMinutes=5,
        Source=source
    )
    code_build = template.add_resource(project)

    write_json_to_file('code_build_template.json', template)

    return template


if __name__ == '__main__':
    create_code_build_template()
