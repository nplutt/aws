from chalice import Chalice
import boto3
from botocore.exceptions import ClientError
import json
import logging
import os

app = Chalice(app_name='data-processing')
app.log.setLevel(logging.DEBUG)

kinesis = boto3.client('kinesis')
aws_lambda = boto3.client('lambda')
s3 = boto3.client('s3')

BUCKET_NAME = os.environ['BUCKET_NAME']
ENVIRONMENT_NAME = os.environ['ENVIRONMENT']
STREAM_NAME = os.environ['STREAM_NAME']


@app.route('/')
def index():
    return {'hello': 'world'}


@app.lambda_function(name='ingress')
def ingress(event, context):
    """
    Handles publishing data to the kinesis stream.
    Args:
        event (dict): {
                        "s3Key": "abc",
                        "index": 2000
                      }
    Returns:
        None
    Throws:
        None
    """
    app.log.info('Triggered by event {}'.format(event))

    key = event['s3Key']
    index = event['index']

    s3_file = get_file_from_s3(key)
    uuids = s3_file[index:]
    records = []

    for x in range(index, index + 5000):
        record = dict(Data=str(uuids[x]),
                      PartitionKey=str(hash(uuids[x])))
        records.append(record)
        if (x % 500) == 0 and x > 0:
            kinesis.put_records(Records=records,
                                StreamName=STREAM_NAME)
            records = []

    aws_lambda.invoke(
        FunctionName='data-processing-ingress-{}'.format(ENVIRONMENT_NAME),
        Payload=json.dumps(
            dict(
                key=key,
                index=index+5000
            )
        )
    )


@app.lambda_function(name='processor')
def processor(event, context):
    """
    Handles processing the data from the kinesis stream.
    Args:
        event (dict): { "s3Key": "abc"}
    Returns:
        None
    Throws:
        None
    """
    app.log.info('Triggered by event {}'.format(event))


def get_file_from_s3(key):
    try:
        s3_file = s3.get_object(Bucket=BUCKET_NAME,
                                Key=key)
    except ClientError as e:
        error_code = int(e.response['Error']['Code'])
        if error_code == 404 or error_code == 403:
            app.log.error('Key {} could not be found S3 returned a status code of {}.'
                          .format(key, error_code))
        else:
            logging.error(e)
        raise

    return s3_file['Body'].read()
