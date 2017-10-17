from setuptools import setup, find_packages
setup(
    name='aws-cloud-formation',
    version='0.0.1',
    description='A package that creates all of my cloud formation scripts for the project.',
    author='Nick Plutt',
    author_email='nplutt@gmail.com',
    install_requires=[
        'boto3>=1.4.3',
        'troposphere>=1.9.1'
    ]
)
