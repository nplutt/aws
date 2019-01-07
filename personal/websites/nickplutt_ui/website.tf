locals {
  bucket_name = "nickplutt-website"
  s3_origin_id = "origin_1"
  domain_name = "nickplutt.com"
}

terraform {
  backend "s3" {
    encrypt = true
    bucket = "nplutt-terraform-state-storage"
    dynamodb_table = "nplutt-terraform-state-lock-dynamo"
    region = "us-west-2"
    key = "websites/nickplutt_ui/terraform.tfstate"
  }
}

provider "aws" {
  region = "us-west-2"
}

provider "aws" {
  alias = "east"
  region = "us-east-1"
}

data "aws_acm_certificate" "nickplutt" {
  provider = "aws.east"
  domain = "${local.domain_name}"
}

data "aws_route53_zone" "nickplutt" {
  name = "${local.domain_name}"
}

resource "aws_s3_bucket" "nickplutt" {
  bucket = "${local.bucket_name}"
  acl = "public-read"

  website {
    index_document = "index.html"
    error_document = "error.html"
  }

  versioning {
    enabled = true
  }
}

resource "aws_s3_bucket_policy" "nickplutt" {
  bucket = "${aws_s3_bucket.nickplutt.id}"
  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Id": "nickplutt-website-bucket-policy",
  "Statement": [
    {
      "Action": [
        "s3:GetObject"
      ],
      "Effect": "Allow",
      "Principal": "*",
      "Resource": "arn:aws:s3:::nickplutt-website/*"
    }
  ]
}
POLICY
}

resource "aws_cloudfront_distribution" "s3_distribution" {
  "aliases" = [
    "${local.domain_name}",
    "www.${local.domain_name}"
  ]

  "default_cache_behavior" {
    target_origin_id = "${local.s3_origin_id}"
    allowed_methods = ["HEAD", "GET"]
    cached_methods = ["HEAD", "GET"]

    "forwarded_values" {
      "cookies" {
        forward = "none"
      }
      query_string = false
    }
    viewer_protocol_policy = "redirect-to-https"
    min_ttl = 0
    max_ttl = 31536000
    default_ttl = 86400
    compress = "true"
  }

  default_root_object = "index.html"
  enabled = true
  http_version = "http2"

  "origin" {
    domain_name = "${aws_s3_bucket.nickplutt.bucket_domain_name}"
    origin_id = "${local.s3_origin_id}"
  }

  price_class = "PriceClass_100"

  custom_error_response {
    error_caching_min_ttl = 86400
    error_code = 404
    response_code = 200
    response_page_path = "/index.html"
  }

  custom_error_response {
    error_caching_min_ttl = 86400
    error_code = 403
    response_code = 200
    response_page_path = "/index.html"
  }

  "restrictions" {
    "geo_restriction" {
      restriction_type = "none"
    }
  }

  "viewer_certificate" {
    acm_certificate_arn = "${data.aws_acm_certificate.nickplutt.arn}"
    minimum_protocol_version = "TLSv1.1_2016"
    ssl_support_method = "sni-only"
  }
}

resource "aws_route53_record" "nickplutt" {
  depends_on = ["aws_cloudfront_distribution.s3_distribution"]
  zone_id = "${data.aws_route53_zone.nickplutt.zone_id}"
  name = "${local.domain_name}"
  type = "A"
   alias {
    evaluate_target_health = false
    name = "${aws_cloudfront_distribution.s3_distribution.domain_name}"
    zone_id = "${aws_cloudfront_distribution.s3_distribution.hosted_zone_id}"
  }
}

resource "aws_route53_record" "www_nickplutt" {
  depends_on = [
    "aws_cloudfront_distribution.s3_distribution"]
  zone_id = "${data.aws_route53_zone.nickplutt.zone_id}"
  name = "www.${local.domain_name}"
  type = "A"
  alias {
    evaluate_target_health = false
    name = "${aws_cloudfront_distribution.s3_distribution.domain_name}"
    zone_id = "${aws_cloudfront_distribution.s3_distribution.hosted_zone_id}"
  }
}