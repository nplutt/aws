from troposphere import Output, Ref, Template, Parameter, GetAtt
from troposphere import ec2
from common import write_json_to_file
from general.vpc.config import vpc_cidr, sub_nets, private_sub_net, nat_gateway


def create_vpc_template(template=None):
    if not template:
        template = Template()
        template.add_description('AWS cloud formation script template.at creates a VPC with a NAT Gg')
        template.add_version('2010-09-09')

    vpc_cidr_block = template.add_parameter(Parameter(
        'VPCCIDR',
        Default=vpc_cidr,
        Description='The IP address space for this VPC, in CIDR notation',
        Type='String',
    ))

    vpc = template.add_resource(ec2.VPC(
        'VPC',
        CidrBlock=Ref(vpc_cidr_block),
    ))

    igw = template.add_resource(ec2.InternetGateway('InternetGateway', ))

    template.add_resource(ec2.VPCGatewayAttachment(
        "NatAttachment",
        VpcId=Ref(vpc),
        InternetGatewayId=Ref(igw),
    ))

    template.add_output(Output(
        'VPCId',
        Value=Ref(vpc),
        Description='VPC Id'
    ))

    for i, sub_net in enumerate(sub_nets):
        public_subnet = template.add_parameter(Parameter(
            'PublicSubnetCidr{}'.format(i),
            Type='String',
            Description='Public Subnet CIDR',
            Default=sub_net['public_cidr'],
        ))

        public_net = template.add_resource(ec2.Subnet(
            'PublicSubnet{}'.format(i),
            AvailabilityZone=sub_net['region'],
            CidrBlock=Ref(public_subnet),
            MapPublicIpOnLaunch=True,
            VpcId=Ref(vpc),
        ))

        public_route_table = template.add_resource(ec2.RouteTable(
            'PublicRouteTable{}'.format(i),
            VpcId=Ref(vpc),
        ))

        template.add_resource(ec2.SubnetRouteTableAssociation(
            'PublicRouteAssociation{}'.format(i),
            SubnetId=Ref(public_net),
            RouteTableId=Ref(public_route_table),
        ))

        template.add_resource(ec2.Route(
            'PublicDefaultRoute{}'.format(i),
            RouteTableId=Ref(public_route_table),
            DestinationCidrBlock='0.0.0.0/0',
            GatewayId=Ref(igw),
        ))

        template.add_output(Output(
            'PublicSubnet{}'.format(i),
            Value=Ref(public_subnet),
            Description='Subnet Id'
        ))

        if private_sub_net:
            private_subnet = template.add_parameter(Parameter(
                'PrivateSubnetCidr{}'.format(i),
                Type='String',
                Description='Private Subnet CIDR',
                Default=sub_net['private_cidr'],
            ))

            private_net = template.add_resource(ec2.Subnet(
                'PrivateSubnet{}'.format(i),
                CidrBlock=Ref(private_subnet),
                MapPublicIpOnLaunch=False,
                VpcId=Ref(vpc),
            ))

            private_route_table = template.add_resource(ec2.RouteTable(
                'PrivateRouteTable{}'.format(i),
                VpcId=Ref(vpc),
            ))

            template.add_resource(ec2.SubnetRouteTableAssociation(
                'PrivateRouteAssociation{}'.format(i),
                SubnetId=Ref(private_net),
                RouteTableId=Ref(private_route_table),
            ))

            template.add_output(Output(
                'PrivateSubnet{}'.format(i),
                Value=Ref(private_subnet),
                Description='Subnet Id'
            ))

        if nat_gateway and private_sub_net:
            nat_eip = template.add_resource(ec2.EIP(
                'NatEip{}'.format(i),
                Domain="vpc",
            ))

            nat = template.add_resource(ec2.NatGateway(
                'Nat{}'.format(i),
                AllocationId=GetAtt(nat_eip, 'AllocationId'),
                SubnetId=Ref(public_net),
            ))

            template.add_resource(ec2.Route(
                'NatRoute{}'.format(i),
                RouteTableId=Ref(private_route_table),
                DestinationCidrBlock='0.0.0.0/0',
                NatGatewayId=Ref(nat),
            ))

            template.add_output(Output(
                'NatEip{}'.format(i),
                Value=Ref(nat_eip),
                Description='Nat Elastic IP',
            ))

    write_json_to_file('vpc.json', template)

if __name__ == '__main__':
    create_vpc_template()
