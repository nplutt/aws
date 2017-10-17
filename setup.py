from setuptools import setup
setup(
    name='aws',
    version='0.0.1',
    description='A package that is used to support using troposphere in bash.',
    author='Nick Plutt',
    author_email='nplutt@gmail.com',
    install_requires=[
        'boto3>=1.4.3',
        'troposphere>=1.9.1',
        'awacs>=0.6.1'
    ]
)
