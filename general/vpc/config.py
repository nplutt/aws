vpc_config = dict(
    name='test-vpc',
    cidr_block='192.168.0.0/16',
    tags=(
        dict(Name='test-vpc')
    )
)

sub_nets = [
    dict(
        region='us-west-2a',
        public_cidr='192.168.0.0/24',
        private_cidr='192.168.1.0/24'
    ),
    dict(
        region='us-west-2b',
        public_cidr='192.168.3.0/24',
        private_cidr='192.168.4.0/24'
    )
]

security_group_config = dict(
    public=dict(
        name='PublicSecurityGroup',
        ingress_rules=[
            dict(port=22,
                 cidr_block='0.0.0.0/0'),
            dict(port=443,
                 cidr_block='0.0.0.0/0'),
            dict(port=80,
                 cidr_block='0.0.0.0/0')
        ]
    ),
    private=dict(
        name='PrivateSecurityGroup',
        ingress_rules=[
            dict(port=5432)
        ]
    )
)

private_sub_net = True
nat_gateway = True

