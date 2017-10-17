from awacs.aws import Action, Allow, Statement, Principal, Policy
from awacs.sts import AssumeRole
from troposphere import Template, Join, Ref, codebuild, iam

from common import write_json_to_file
from config import props
from s3.artifacts.config import props as s3_artifact_props
from s3.nickplutt_com.config import props as s3_nickplutt_com_props


def create_code_build_template(template=None):
    if not template:
        template = Template()
        template.add_description('This CloudFormation template creates a build for the apartments main ui.')
        template.add_version('2010-09-09')

    code_build_role = template.add_resource(
        iam.Role(
            props.get('role_name'),
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
            props.get('profile_name'),
            Path='/service-role/',
            Roles=[Ref(code_build_role)]
        )
    )

    code_build_role_policies = template.add_resource(
        iam.ManagedPolicy(
            props.get('policy_name'),
            PolicyDocument=Policy(
                Version='2012-10-17',
                Statement=[
                    Statement(
                        Effect=Allow,
                        Resource=[
                            Join(':', ['arn:aws:logs', Ref('AWS::Region'), Ref('AWS::AccountId'),
                                       'log-group:/aws/codebuild/{}'.format(props.get('code_build_name'))]),
                            Join(':', ['arn:aws:logs', Ref('AWS::Region'), Ref('AWS::AccountId'),
                                       'log-group:/aws/codebuild/{}'.format(props.get('code_build_name')), '*'])
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
                            'arn:aws:s3:::' + s3_artifact_props.get('bucket_name') + '/*',
                            'arn:aws:s3:::' + s3_nickplutt_com_props.get('bucket_name') + '/*'
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
        Name=props.get('code_build_name'),
        Location=s3_artifact_props.get('bucket_name'),
        Packaging='zip'
    )

    environment = codebuild.Environment(
        ComputeType='BUILD_GENERAL1_SMALL',
        Image=props.get('docker_image'),
        Type='LINUX_CONTAINER',
        EnvironmentVariables=[
            codebuild.EnvironmentVariable(
                Name='CHROME_BIN',
                Value='/serverless-chrome/chrome/headless-chrome/headless_shell'
            ),
            codebuild.EnvironmentVariable(
                Name='BUCKET',
                Value=s3_nickplutt_com_props.get('bucket_name')
            )
        ]
    )

    source = codebuild.Source(
        Location=props.get('repo_url'),
        Type='GITHUB'
    )

    project = codebuild.Project(
        props.get('code_build_name'),
        Artifacts=artifacts,
        Environment=environment,
        Name=props.get('code_build_name'),
        ServiceRole=Ref(code_build_role),
        TimeoutInMinutes=10,
        Source=source
    )
    code_build = template.add_resource(project)

    write_json_to_file('ui_pipeline.json', template)

    return template


if __name__ == '__main__':
    create_code_build_template()
