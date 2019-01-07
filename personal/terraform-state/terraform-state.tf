provider "aws" {
  region                  = "us-west-2"
}

resource "aws_s3_bucket" "s3-terraform-state-storage" {
  bucket = "nplutt-terraform-state-storage"
  versioning {
    enabled = true
  }
  lifecycle {
    prevent_destroy = true
  }
  tags {
    Name = "nplutt-s3-terraform-state-storage",
    Environment = "prod",
    Project = "personal"
  }
}

resource "aws_dynamodb_table" "dynamodb-terraform-state-lock" {
  name = "nplutt-terraform-state-lock-dynamo"
  hash_key = "LockID"
  read_capacity = 20
  write_capacity = 20
  attribute {
    name = "LockID"
    type = "S"
  }
  tags {
    Name = "nplutt-dynamodb-terraform-state-storage",
    Environment = "prod",
    Project = "personal"
  }
}

