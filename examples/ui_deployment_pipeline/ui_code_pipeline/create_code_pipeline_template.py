from awacs.aws import Action, Allow, Statement, Principal, Policy
from awacs.sts import AssumeRole
from troposphere import GetAtt, Ref, Template, codepipeline, iam

import create_code_build_template
from ui_integrated_deployment.common import write_json_to_file
from ui_integrated_deployment.properties import (region, account_number, ui_codebuild_project_name, codebuild_bucket_name,
                                                 ui_repo_owner, ui_repo_name, ui_branch, github_oauth_token,
                                                 ui_pipeline_project_name, ui_pipeline_role_name, ui_pipeline_instance_profile,
                                                 ui_pipeline_policy)


def create_code_pipeline(template=None):
    if not template:
        template = Template()
        template.add_description('This CloudFormation template creates a build pipeline for an angular2 build.')
        template.add_version('2010-09-09')

    template = create_code_build_template.create_code_build_template(template)

    code_pipeline_role = template.add_resource(
        iam.Role(
            ui_pipeline_role_name,
            AssumeRolePolicyDocument=Policy(
                Statement=[
                    Statement(
                        Action=[AssumeRole],
                        Effect='Allow',
                        Principal=Principal('Service', ['codepipeline.amazonaws.com', 'codebuild.amazonaws.com'])
                    )
                ]
            )
        )
    )

    code_pipeline_instance_profile = template.add_resource(
        iam.InstanceProfile(
            ui_pipeline_instance_profile,
            Path='/',
            Roles=[Ref(code_pipeline_role)]
        )
    )

    code_pipeline_role_policies = template.add_resource(
        iam.ManagedPolicy(
            ui_pipeline_policy,
            PolicyDocument=Policy(
                Version='2012-10-17',
                Statement=[
                    Statement(
                        Effect=Allow,
                        Resource=[
                            'arn:aws:s3:::' + codebuild_bucket_name + '/*'
                        ],
                        Action=[
                            Action('s3', 'PutObject')
                        ]
                    ),
                    Statement(
                        Effect=Allow,
                        Resource=[
                            'arn:aws:codebuild:' + region + ':' + account_number + ':project/' + ui_codebuild_project_name
                        ],
                        Action=[
                            Action('codebuild', 'BatchGetBuilds'),
                            Action('codebuild', 'StartBuild')
                        ]
                    )
                ]
            ),
            Roles=[Ref(code_pipeline_role)]
        )
    )

    pipeline = codepipeline.Pipeline(
        ui_pipeline_project_name,
        Name=ui_pipeline_project_name,
        RoleArn=GetAtt(ui_pipeline_role_name, 'Arn'),
        Stages=[
            codepipeline.Stages(
                Name='Source',
                Actions=[
                    codepipeline.Actions(
                        Name='Source',
                        ActionTypeId=codepipeline.ActionTypeID(
                            Category='Source',
                            Owner='ThirdParty',
                            Version='1',
                            Provider='GitHub'
                        ),
                        OutputArtifacts=[
                            codepipeline.OutputArtifacts(
                                Name='MyApp'
                            )
                        ],
                        Configuration={
                            'Owner': ui_repo_owner,
                            'Repo': ui_repo_name,
                            'Branch': ui_branch,
                            'OAuthToken': github_oauth_token
                        },
                        RunOrder='1'
                    )
                ]
            ),
            codepipeline.Stages(
                Name='Build',
                Actions=[
                    codepipeline.Actions(
                        Name='Build',
                        InputArtifacts=[
                            codepipeline.InputArtifacts(
                                Name='MyApp'
                            )
                        ],
                        OutputArtifacts=[
                            codepipeline.OutputArtifacts(
                                Name='MyAppBuild'
                            )
                        ],
                        ActionTypeId=codepipeline.ActionTypeID(
                            Category='Build',
                            Owner='AWS',
                            Version='1',
                            Provider='CodeBuild'
                        ),
                        Configuration={
                            'ProjectName': ui_codebuild_project_name
                        },
                        RunOrder='2'
                    )
                ]
            )
        ],
        ArtifactStore=codepipeline.ArtifactStore(
            Type='S3',
            Location=codebuild_bucket_name
        )
    )

    template.add_resource(pipeline)

    write_json_to_file('code_pipeline_template.json', template)


if __name__ == '__main__':
    create_code_pipeline()
