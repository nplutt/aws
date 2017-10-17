vpc_cidr = '192.168.0.0/20'
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
private_sub_net = False,
nat_gateway = False

