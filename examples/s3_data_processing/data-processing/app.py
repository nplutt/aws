from chalice import Chalice
import base64
import boto3
from botocore.exceptions import ClientError
from calendar import timegm
import json
import logging
import os
from time import sleep, gmtime
from uuid import uuid4

app = Chalice(app_name='data-processing')
app.log.setLevel(logging.DEBUG)

kinesis = boto3.client('kinesis')
aws_lambda = boto3.client('lambda')
s3 = boto3.client('s3')

BUCKET_NAME = os.environ.get('BUCKET_NAME')
ENVIRONMENT_NAME = os.environ.get('ENVIRONMENT')
STREAM_NAME = os.environ.get('STREAM_NAME')
CONTAINER_ID = str(uuid4())

# 4 shards: Start 1515556667; End 1515557445; Processed 6500; Time 1079 sec; avg 6.024 r/s
# 10 shards: Start 1515878894; End 1515879838; Processed 30,000; Time 944 sec; avg 31.7 r/s


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

    s3_file = get_file_from_s3(key).splitlines()
    uuids = s3_file[index:]
    records = []
    num_to_process = 5000 if len(uuids) >= 5000 else len(uuids) - index

    for x in range(0, index + num_to_process):
        uuid = uuids[x]
        s3_key = '{}/{}/{}/{}/{}.txt'.format(uuid[0], uuid[1], uuid[2], uuid[3], uuid)
        record = dict(Data=json.dumps({'s3Key': s3_key}),
                      PartitionKey=str(hash(uuids[x])))
        records.append(record)

        if ((len(records) % 200) == 0 and len(records) > 0) or len(records) == num_to_process:
            app.log.info('Placing {} records into {} kinesis stream.'.format(len(records), STREAM_NAME))
            kinesis.put_records(Records=records,
                                StreamName=STREAM_NAME)
            records = []
            sleep(.1)  # Sleep 1 second so as to not go over the single kinesis shard write limit of 1000

    if num_to_process == 5000:
        app.log.info('Invoking lambda to continue feeding data into kinesis.')
        aws_lambda.invoke(
            FunctionName='data-processing-{}-ingress'.format(ENVIRONMENT_NAME),
            Payload=json.dumps(
                dict(
                    s3Key=key,
                    index=index+5000
                )
            ),
            InvocationType='Event'
        )


@app.lambda_function(name='processor')  # 1 Lambda per kinesis shard
def processor(event, context):
    """
    Handles processing the data from the kinesis stream.
    Args:
        event (dict):{
                        "Records": [
                          {
                            "eventID": "shardId-000000000000:49545115243490985018280067714973144582180062593244200961",
                            "eventVersion": "1.0",
                            "kinesis": {
                              "partitionKey": "partitionKey-3",
                              "data": "SGVsbG8sIHRoaXMgaXMgYSB0ZXN0IDEyMy4=",
                              "kinesisSchemaVersion": "1.0",
                              "sequenceNumber": "49545115243490985018280067714973144582180062593244200961"
                            },
                            "invokeIdentityArn": identityarn,
                            "eventName": "aws:kinesis:record",
                            "eventSourceARN": eventsourcearn,
                            "eventSource": "aws:kinesis",
                            "awsRegion": "us-east-1"
                          }
                        ]
                     }


    Returns:
        None
    Throws:
        None
    """
    app.log.info('Container {} started at {} seconds since epoc'.format(CONTAINER_ID, timegm(gmtime())))
    records = event['Records']

    for record in records:
        try:
            data = base64.b64decode(record['kinesis']['data'])
            key = json.loads(data)['s3Key']
            body = get_file_from_s3(key)

            sleep(.1)  # This is here to represent what ever data processing needs to be done

            put_file_to_s3(key, body)
            app.log.info('Successfully processed file {}.'.format(key))
        except Exception as e:
            app.log.error("Caught exception of {} when trying to process record {}."
                          .format(e, record))

    app.log.info('Container {} ended at {} seconds since epoc'.format(CONTAINER_ID, timegm(gmtime())))


def get_file_from_s3(key):
    try:
        s3_file = s3.get_object(Bucket=BUCKET_NAME, Key=key)
        return s3_file['Body'].read()
    except ClientError as e:
        app.log.error('Error of {} happened when retrieving file {} from bucket {}.'
                      .format(e, key, BUCKET_NAME))


def put_file_to_s3(key, body):
    try:
        s3.put_object(
            Body=body,
            Bucket=BUCKET_NAME,
            Key=key
        )
    except ClientError as e:
        app.log.error('Error of {} happened when uploading file {} to bucket {}.'
                      .format(e, key, BUCKET_NAME))
