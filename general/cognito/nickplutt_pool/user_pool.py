from troposphere import Template, Ref
from troposphere.cognito import UserPool, PasswordPolicy, Policies, UserPoolClient, SchemaAttribute
from common import write_json_to_file
from general.cognito.nickplutt_pool.config import (user_pool_name, auto_verified_attributes, email_verification_message,
                                                   email_verification_subject, pool_clients, schema_attributes)


def create_cognito_user_pool(template=None):
    if not template:
        template = Template()
        template.add_description('This cloudformation template creates a cognito user pool')
        template.add_version('2010-09-09')

    user_pool = template.add_resource(
        UserPool(
            user_pool_name,
            UserPoolName=user_pool_name,
            AutoVerifiedAttributes=auto_verified_attributes,
            Policies=Policies(
                PasswordPolicy=PasswordPolicy(
                    MinimumLength=8,
                    RequireLowercase=True,
                    RequireNumbers=True,
                    RequireSymbols=True,
                    RequireUppercase=True
                )
            ),
            EmailVerificationMessage=email_verification_message,
            EmailVerificationSubject=email_verification_subject,
            Schema=create_schema_attributes()
        )
    )

    for pool_client in pool_clients:
        template.add_resource(
            UserPoolClient(
                pool_client.get('client_name'),
                ClientName=pool_client.get('client_name'),
                GenerateSecret=pool_client.get('generate_secret'),
                RefreshTokenValidity=pool_client.get('refresh_token_validity'),
                UserPoolId=Ref(user_pool)
            )
        )

    write_json_to_file('user_pool.json', template)


def create_schema_attributes():
    attributes = []
    for attribute in schema_attributes:
        attributes.append(
            SchemaAttribute(
                Name=attribute.get('name'),
                Required=attribute.get('required')
            )
        )

    return attributes


if __name__ == '__main__':
    create_cognito_user_pool()
