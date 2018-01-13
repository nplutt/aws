import boto3


s3 = boto3.client('s3')
BUCKET_NAME = 'data-processing-example-nplutt'

if __name__ == '__main__':
    uuids = None
    number_uuids = 30000

    with open('uuid.txt', 'rb') as f:
        s3.upload_fileobj(f, BUCKET_NAME, 'uuid.txt')
        print('Uploaded uuid.txt to bucket')

    with open('s3_data.txt', 'rb') as f:
        s3.upload_fileobj(f, BUCKET_NAME, 's3_data.txt')
        print('Uploaded s3_data.txt to bucket')

    with open('uuid.txt', 'rb') as f:
        content = f.readlines()
        uuids = [x.strip() for x in content]

    for index, uuid in enumerate(uuids):
        key = '{}/{}/{}/{}/{}.txt'.format(uuid[0], uuid[1], uuid[2], uuid[3], uuid)
        s3.copy_object(
            Bucket=BUCKET_NAME,
            CopySource=dict(
                Bucket=BUCKET_NAME,
                Key='s3_data.txt'
            ),
            Key=key
        )

        print('{}: Copied {} to bucket key {}'.format(index, uuid, key))

        if index >= number_uuids:
            break
