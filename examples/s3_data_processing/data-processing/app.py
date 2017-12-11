from chalice import Chalice
import boto3
import logging

app = Chalice(app_name='data-processing')
app.log.setLevel(logging.DEBUG)

kinesis = boto3.client('kinesis')
lam = boto3.client('lambda')
s3 = boto3.client('s3')


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

