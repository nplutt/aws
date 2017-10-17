from troposphere import Template, s3
from common import write_json_to_file
from config import props


def create_s3_buckets(template=None):
    if not template:
        template = Template()
        template.add_description('This cloudformation template creates an s3 bucket for build artifacts')
        template.add_version('2010-09-09')

    code_bucket = s3.Bucket(
        props.get('resource_name'),
        BucketName=props.get('bucket_name'),
        VersioningConfiguration=s3.VersioningConfiguration(
            Status='Enabled'
        )
    )

    template.add_resource(code_bucket)

    write_json_to_file('artifacts_bucket.json', template)


if __name__ == '__main__':
    create_s3_buckets()
