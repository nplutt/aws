from troposphere import Template
from troposphere.kinesis import Stream
from common import write_json_to_file
from general.kinesis.streams.config import stream_params


def create_stream():
    template = Template()

    template.add_resource(
        Stream(
            "Stream1",
            Name=stream_params['stream_name'],
            ShardCount=stream_params['shard_count']
        )
    )

    write_json_to_file('stream.json', template)

if __name__ == '__main__':
    create_stream()
