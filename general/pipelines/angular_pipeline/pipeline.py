from awacs.aws import Action, Allow, Statement, Principal, Policy
from awacs.sts import AssumeRole
from troposphere import Template, Join, Ref, codebuild, iam

from common import write_json_to_file
from general.pipelines.angular_pipeline.config import (role_name, profile_name, policy_name, code_build_name, repo_url,
                                                       docker_image)
from general.s3.artifacts.config import bucket_name as artifact_bucket_name
from general.s3.website_name_com.config import bucket_name as website_name_com_bucket_name


def create_code_build_template(template=None):
    if not template:
        template = Template()
        template.add_description('This CloudFormation template creates a build pipeline for an angular application.')
        template.add_version('2010-09-09')

    code_build_role = template.add_resource(
        iam.Role(
            role_name,
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
            profile_name,
            Path='/service-role/',
            Roles=[Ref(code_build_role)]
        )
    )

    code_build_role_policies = template.add_resource(
        iam.ManagedPolicy(
            policy_name,
            PolicyDocument=Policy(
                Version='2012-10-17',
                Statement=[
                    Statement(
                        Effect=Allow,
                        Resource=[
                            Join(':', ['arn:aws:logs', Ref('AWS::Region'), Ref('AWS::AccountId'),
                                       'log-group:/aws/codebuild/{}'.format(code_build_name)]),
                            Join(':', ['arn:aws:logs', Ref('AWS::Region'), Ref('AWS::AccountId'),
                                       'log-group:/aws/codebuild/{}'.format(code_build_name), '*'])
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
                            'arn:aws:s3:::' + artifact_bucket_name + '/*',
                            'arn:aws:s3:::' + website_name_com_bucket_name + '/*'
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
        Name=code_build_name,
        Location=artifact_bucket_name,
        Packaging='zip'
    )

    environment = codebuild.Environment(
        ComputeType='BUILD_GENERAL1_SMALL',
        Image=docker_image,
        Type='LINUX_CONTAINER',
        EnvironmentVariables=[
            codebuild.EnvironmentVariable(
                Name='BUCKET',
                Value=website_name_com_bucket_name
            )
        ]
    )

    source = codebuild.Source(
        Location=repo_url,
        Type='GITHUB'
    )

    project = codebuild.Project(
        code_build_name,
        Artifacts=artifacts,
        Environment=environment,
        Name=code_build_name,
        ServiceRole=Ref(code_build_role),
        TimeoutInMinutes=10,
        Source=source
    )
    code_build = template.add_resource(project)

    write_json_to_file('pipeline.json', template)

    return template


if __name__ == '__main__':
    create_code_build_template()
    print('code_build_name: {}'.format(code_build_name))
