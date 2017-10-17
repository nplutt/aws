from troposphere import Template, s3, Ref
from awacs.aws import Action, Allow
from awacs.aws import Policy, Statement, Principal
import awacs.s3 as _s3
from ui_integrated_deployment.common import write_json_to_file
from ui_integrated_deployment.properties import codebuild_bucket_name, website_bucket_name


def create_s3_buckets(template=None):
    if not template:
        template = Template()
        template.add_description('This cloudformation template creates an s3 bucket for hosting a static website')
        template.add_version('2010-09-09')

    web_bucket = s3.Bucket(
        website_bucket_name,
        BucketName=website_bucket_name,
        AccessControl=s3.PublicRead,
        WebsiteConfiguration=s3.WebsiteConfiguration(
            IndexDocument='index.html',
            ErrorDocument='error.html'
        ),
        VersioningConfiguration=s3.VersioningConfiguration(
            Status='Enabled'
        )
    )

    web_bucket = template.add_resource(web_bucket)

    code_bucket = s3.Bucket(
        codebuild_bucket_name,
        BucketName=codebuild_bucket_name,
        VersioningConfiguration=s3.VersioningConfiguration(
            Status='Enabled'
        )
    )

    template.add_resource(code_bucket)

    pd = Policy(
        Statement=[
            Statement(
                Action=[Action('s3', 'GetObject')],
                Effect=Allow,
                Resource=['arn:aws:s3:::' + website_bucket_name + '/*'],
                Principal=Principal('*')
            ),
        ],
    )

    template.add_resource(s3.BucketPolicy(
        "BucketPolicy",
        Bucket=Ref(web_bucket),
        PolicyDocument=pd
    ))

    write_json_to_file('s3_buckets_template.json', template)


if __name__ == '__main__':
    create_s3_buckets()
