import boto3


s3 = boto3.client('s3')

if __name__ == '__main__':
    uuids = None
    number_uuids = 1000

    with open('uuid.txt', 'rb') as f:
        s3.upload_fileobj(f, 'data-processing-example-nplutt', 'uuid.txt')
        print('Uploaded uuid.txt to bucket')

    with open('uuid.txt', 'rb') as f:
        content = f.readlines()
        uuids = [x.strip() for x in content]

    for index, uuid in enumerate(uuids):
        with open('s3_data.txt', 'rb') as data:
            key = '{}/{}/{}/{}/{}.txt'.format(uuid[0], uuid[1], uuid[2], uuid[3], uuid)
            s3.upload_fileobj(data, 'data-processing-example-nplutt', key)
            print('{} uploaded {} to bucket'.format(index, uuid))

        if index >= number_uuids:
            break
