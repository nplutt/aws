from troposphere import Template, s3, Ref
from awacs.aws import Action, Allow
from awacs.aws import Policy, Statement, Principal
from common import write_json_to_file
from general.s3.www_nickplutt_com.config import resource_name, bucket_name
from general.s3.nickplutt_com.config import bucket_name as nickplutt_com_bucket_name


def create_s3_buckets(template=None):
    if not template:
        template = Template()
        template.add_description('This cloudformation template creates an s3 bucket for hosting a static website')
        template.add_version('2010-09-09')

    web_bucket = s3.Bucket(
        resource_name,
        BucketName=bucket_name,
        AccessControl=s3.PublicRead,
        WebsiteConfiguration=s3.WebsiteConfiguration(
            RedirectAllRequestsTo=s3.RedirectAllRequestsTo(
                HostName=nickplutt_com_bucket_name
            )
        ),
        VersioningConfiguration=s3.VersioningConfiguration(
            Status='Enabled'
        )
    )

    web_bucket = template.add_resource(web_bucket)

    pd = Policy(
        Statement=[
            Statement(
                Action=[Action('s3', 'GetObject')],
                Effect=Allow,
                Resource=['arn:aws:s3:::' + bucket_name + '/*'],
                Principal=Principal('*')
            ),
        ],
    )

    template.add_resource(s3.BucketPolicy(
        "BucketPolicy",
        Bucket=Ref(web_bucket),
        PolicyDocument=pd
    ))

    write_json_to_file('www_nickplutt_bucket.json', template)


if __name__ == '__main__':
    create_s3_buckets()
