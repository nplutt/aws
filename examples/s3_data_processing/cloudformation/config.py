s3_params = dict(
    bucket_name='data-processing-example-nplutt'
)

kinesis_params = dict(
    stream_name='data-processing-example',
    shard_count=1
)

lambda_iam_params = dict(
    role_name='lambda-data-processing-example'
)
