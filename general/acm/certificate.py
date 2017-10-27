from troposphere import Template
from troposphere.certificatemanager import Certificate, DomainValidationOption
from common import write_json_to_file
from general.acm.config import tag_name, domain_name, additional_names


def create_certificate(template=None):
    if not template:
        template = Template()
        template.add_description('This CloudFormation template creates a certificate for domainname.com')
        template.add_version('2010-09-09')

    template.add_resource(
        Certificate(
            tag_name,
            DomainName=domain_name,
            DomainValidationOptions=[
                DomainValidationOption(
                    DomainName=domain_name,
                    ValidationDomain=domain_name,
                ),
            ],
            SubjectAlternativeNames=additional_names
        )
    )

    write_json_to_file('certificate.json', template)


if __name__ == '__main__':
    create_certificate()
