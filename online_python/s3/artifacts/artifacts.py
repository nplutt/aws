from troposphere import Template, Join, Ref
from troposphere.s3 import Bucket, VersioningConfiguration, NotificationConfiguration, LambdaConfigurations
from common import write_json_to_file
from online_python.s3.artifacts.config import resource_name, bucket_name, lambda_name


def create_s3_buckets(template=None):
    if not template:
        template = Template()
        template.add_description('This cloudformation template creates an s3 bucket for build artifacts')
        template.add_version('2010-09-09')

    code_bucket = Bucket(
        resource_name,
        BucketName=bucket_name,
        VersioningConfiguration=VersioningConfiguration(
            Status='Enabled'
        ),
        NotificationConfiguration=NotificationConfiguration(
            LambdaConfigurations=[
                    LambdaConfigurations(
                       Event='s3:ObjectCreated:Put',
                       Function=Join(':', ['arn', 'aws', 'lambda', Ref('AWS::Region'), Ref('AWS::AccountId'),
                                           'function', lambda_name])
                )
            ]
        )
    )

    template.add_resource(code_bucket)

    write_json_to_file('artifacts_bucket.json', template)


if __name__ == '__main__':
    create_s3_buckets()
