from uuid import uuid4


if __name__ == '__main__':
    number_uuids = 1000
    number_records = 150000
    uuids = []

    with open('uuid.txt', 'a') as f:
        for x in range(0, 1000):
            uuid = uuid4()
            uuids.append(uuid)
            f.write(str(uuid4()) + '\n')

        for x in range(0, number_records/number_uuids - 1):
            for u in uuids:
                f.write(str(u) + '\n')

    with open('s3_data.txt', 'a') as f:
        for x in range(0, 40):
            for u in uuids:
                f.write(str(u) + "\n")
