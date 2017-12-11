from awacs.aws import Action, Allow, Statement, Policy, Principal
from awacs.sts import AssumeRole
from troposphere import Template, kinesis, s3, iam, Ref, Join

from common import write_json_to_file
from examples.s3_data_processing.cloudformation.config import (s3_params, kinesis_params, lambda_iam_params)


def create_cloudformation_template():
    template = Template()
    template.add_description('This CloudFormation template creates a all of the builds for py-online.')
    template.add_version('2010-09-09')

    template = create_s3_bucket(template)
    template = create_kinesis_stream(template)
    template = create_lambda_iam_role(template)

    write_json_to_file('stack.json', template)


def create_s3_bucket(template):
    bucket = s3.Bucket(
        'DataProcessingBucketNplutt',
        BucketName=s3_params['bucket_name'],
        VersioningConfiguration=s3.VersioningConfiguration(
            Status='Enabled'
        )
    )
    template.add_resource(bucket)

    return template


def create_kinesis_stream(template):
    stream = kinesis.Stream(
        "Stream1",
        Name=kinesis_params['stream_name'],
        ShardCount=kinesis_params['shard_count']
    )
    template.add_resource(stream)
    return template


def create_lambda_iam_role(template):
    role = iam.Role(
        'LambdaDataProcessingRole',
        RoleName=lambda_iam_params['role_name'],
        AssumeRolePolicyDocument=Policy(
            Statement=[
                Statement(
                    Action=[AssumeRole],
                    Effect='Allow',
                    Principal=Principal('Service', ['lambda.amazonaws.com'])
                )
            ]
        )
    )
    template.add_resource(role)

    instance_profile = iam.InstanceProfile(
        'LambdaDataProcessingProfile',
        Path='/service-role/',
        Roles=[Ref(role)]
    )
    template.add_resource(instance_profile)

    cloudwatch_statement = Statement(
        Effect=Allow,
        Resource=[
            Join(':', ['arn:aws:logs',
                       Ref('AWS::Region'),
                       Ref('AWS::AccountId'),
                       'log-group:/aws/*']
                 )
        ],
        Action=[
            Action('logs', 'CreateLogGroup'),
            Action('logs', 'CreateLogStream'),
            Action('logs', 'PutLogEvents')
        ]
    )

    lambda_statement = Statement(
        Effect=Allow,
        Resource=[
            Join(':', ['arn',
                       'aws',
                       'lambda',
                       Ref('AWS::Region'),
                       Ref('AWS::AccountId'),
                       'function',
                       '*'])
        ],
        Action=[
            Action('lambda', 'InvokeFunction')
        ]
    )

    s3_statement = Statement(
        Effect=Allow,
        Resource=[
            'arn:aws:s3:::{}/*'.format(s3_params['bucket_name'])
        ],
        Action=[
            Action('s3', 'GetObject'),
            Action('s3', 'PutObject')
        ]
    )

    managed_policy = iam.ManagedPolicy(
        'LambdaDataProcessingPolicy',
        PolicyDocument=Policy(
            Version='2012-10-17',
            Statement=[
                cloudwatch_statement,
                lambda_statement,
                s3_statement
            ]
        )
    )
    template.add_resource(managed_policy)

    return template


if __name__ == '__main__':
    create_cloudformation_template()
