terraform {
  backend "s3" {
    encrypt = true
    bucket = "nplutt-terraform-state-storage"
    dynamodb_table = "nplutt-terraform-state-lock-dynamo"
    region = "us-west-2"
    key = "acm/terraform.tfstate"
  }
}

provider "aws" {
  region = "us-east-1"
}

data "aws_route53_zone" "nickplutt" {
  name = "nickplutt.com"
}

resource "aws_acm_certificate" "nickplutt" {
  domain_name       = "nickplutt.com"
  subject_alternative_names = [
     "*.nickplutt.com"
  ]
  validation_method = "DNS"

  tags = {
    Name = "nickplutt.com",
    Environment = "prod",
    Project = "personal"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route53_record" "nickplutt_cert_validation" {
  name = "${aws_acm_certificate.nickplutt.domain_validation_options.0.resource_record_name}"
  type = "${aws_acm_certificate.nickplutt.domain_validation_options.0.resource_record_type}"
  zone_id = "${data.aws_route53_zone.nickplutt.zone_id}"
  records = [
    "${aws_acm_certificate.nickplutt.domain_validation_options.0.resource_record_value}"
  ]
  ttl = 60
}
