from awacs.aws import Action, Allow, Statement, Principal, Policy
from awacs.sts import AssumeRole
from troposphere import Template, Ref, iam

from ui_integrated_deployment.common import write_json_to_file
from ui_integrated_deployment.properties import (lambda_role_name, lambda_policy_name,
                                                 lambda_profile_name, website_bucket_name, codebuild_bucket_name)


def create_lambda_iam_template(template=None):
    if not template:
        template = Template()
        template.add_description('This CloudFormation template creates a build for an angular2 build.')
        template.add_version('2010-09-09')

    lambda_role = template.add_resource(
        iam.Role(
            lambda_role_name,
            RoleName=lambda_role_name,
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
    )

    lambda_profile = template.add_resource(
        iam.InstanceProfile(
            lambda_profile_name,
            Path='/service-role/',
            Roles=[Ref(lambda_role)]
        )
    )

    lambda_policy = template.add_resource(
        iam.ManagedPolicy(
            lambda_policy_name,
            PolicyDocument=Policy(
                Version='2012-10-17',
                Statement=[
                    Statement(
                        Effect=Allow,
                        Resource=[
                            'arn:aws:s3:::' + website_bucket_name + '/*',
                            'arn:aws:s3:::' + codebuild_bucket_name + '/*'
                        ],
                        Action=[
                            Action('s3', '*')
                        ]
                    )
                ]
            ),
            Roles=[Ref(lambda_role)]
        )
    )

    write_json_to_file('lambda_iam_role.json', template)

    return template


if __name__ == '__main__':
    create_lambda_iam_template()
