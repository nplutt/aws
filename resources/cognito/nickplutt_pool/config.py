user_pool_name = 'nickpltt'
auto_verified_attributes = ['email']
email_verification_message = 'Your verification code is {####}.'
email_verification_subject = 'Your verification code'
pool_clients = [
    dict(
        client_name='web',
        generate_secret=False,
        refresh_token_validity=30
    )
]
schema_attributes = [
    dict(
        name='email',
        required='true'
    )
]
