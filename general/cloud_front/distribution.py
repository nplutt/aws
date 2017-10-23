from troposphere import Parameter, Ref, Template
from troposphere.cloudfront import (DefaultCacheBehavior, Distribution, DistributionConfig, ForwardedValues, Origin, S3Origin,
                                    ViewerCertificate)
from common import write_json_to_file
from general.cloud_front.config import (s3_dns_name, distribution_name, origin_id, viewer_protocol_policy,
                                              allowed_methods, min_ttl, max_ttl, default_ttl, compress_objects,
                                              price_class, alternate_domain_names, certificate_arn, default_root_object,
                                              enabled)


def create_distribution_template(template=None):
    if not template:
        template = Template()
        template.add_description('This CloudFormation template creates a cloudfront distribution for a static website '
                                 'hosted out of s3.')
        template.add_version('2010-09-09')

    distribution = template.add_resource(
        Distribution(
            distribution_name,
            DistributionConfig=DistributionConfig(
                Origins=[
                    Origin(
                        Id=origin_id,
                        DomainName=s3_dns_name,
                        S3OriginConfig=S3Origin()
                    )
                ],
                DefaultCacheBehavior=DefaultCacheBehavior(
                    TargetOriginId=origin_id,
                    ViewerProtocolPolicy=viewer_protocol_policy,
                    AllowedMethods=allowed_methods,
                    MinTTL=min_ttl,
                    MaxTTL=max_ttl,
                    DefaultTTL=default_ttl,
                    Compress=compress_objects,
                    ForwardedValues=ForwardedValues(
                        QueryString=False
                    )
                ),
                PriceClass=price_class,
                Aliases=alternate_domain_names,
                ViewerCertificate=ViewerCertificate(
                    AcmCertificateArn=certificate_arn,
                    SslSupportMethod='sni-only',
                    MinimumProtocolVersion='TLSv1.1_2016'
                ),
                HttpVersion='http2',
                DefaultRootObject=default_root_object,
                Enabled=enabled
            )
        )
    )

    # print template.to_json()
    write_json_to_file('distribution.json', template)


if __name__ == '__main__':
    create_distribution_template()
