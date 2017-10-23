from os import environ


s3_dns_name = 'bucket.s3.amazonaws.com'
distribution_name = 'generaldistribution'
origin_id = 'origin_1'
viewer_protocol_policy = 'redirect-to-https'
allowed_methods = ['HEAD', 'GET']
min_ttl = 0
max_ttl = 31536000
default_ttl = 86400
compress_objects = True
price_class = 'PriceClass_100'
alternate_domain_names = []
certificate_arn = environ['CERT_ARN']
default_root_object = 'index.html'
enabled = True
