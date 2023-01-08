provider "aws" {
  region              = "us-east-1"
  
  default_tags {
    tags = {
      Owner       = "Mark"
      Environment = "Development"
      Department  = "Finance"
    }
  }
}

locals {
  bucket_arn = "arn:aws:s3:::all-human-beings-are-born-free-and-equal-in-dignity-and-rights"
}

/*
Example: Creating IAM role, policy, and attaching policy to the role

- IAM Role will comply with all the tags.
- IAM Policy will comply will all the tags
*/

resource "aws_iam_role" "role_1" {
  name               = "example_role1"
  assume_role_policy = data.aws_iam_policy_document.assume_policy_1.json

  tags = {
    Compliance = "PCI"
  }
}

data "aws_iam_policy_document" "assume_policy_1" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_policy" "policy_1" {
  name   = "example_policy_1"
  path   = "/"
  policy = data.aws_iam_policy_document.document_1.json

  tags = {
    Compliance  = "PCI"
    Version     = "1"
    Description = "Some important description"
  }
}

data "aws_iam_policy_document" "document_1" {
  statement {
    sid       = "AllowedActionsOnBucket"
    actions   = ["s3:*"]
    resources = [local.bucket_arn]
  }
}

resource "aws_iam_role_policy_attachment" "policy_attachment_1" {
  role       = aws_iam_role.role_1.name
  policy_arn = aws_iam_policy.policy_1.arn
}

/* 
Example: Adding IAM Policy to an existing role

- IAM Policy will not comply with all the tags
*/


resource "aws_iam_policy" "policy_1_1" {
  name   = "example_policy_1_1"
  path   = "/"
  policy = data.aws_iam_policy_document.document_1.json

  tags = {
    Compliance = "PCI"
    Version    = "1"
  }
}


resource "aws_iam_role_policy_attachment" "policy_attachment_1_1" {
  role       = aws_iam_role.role_1.name
  policy_arn = aws_iam_policy.policy_1_1.arn
}

/*
Example: Creating IAM role and attaching inline policy to the role

- IAM Role will not comply with all the tags.
- Inline policy does not have an ARN and will be ignored
*/


resource "aws_iam_role" "role_2" {
  name               = "example_role2"
  assume_role_policy = data.aws_iam_policy_document.assume_policy_2.json
}

data "aws_iam_policy_document" "assume_policy_2" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy" "policy_2" {
  name   = "example_policy_2"
  role   = aws_iam_role.role_2.id
  policy = data.aws_iam_policy_document.document_2.json
}

data "aws_iam_policy_document" "document_2" {
  statement {
    sid       = "DeniedActionsOnBucket"
    effect    = "Deny"
    actions   = ["s3:*"]
    resources = [local.bucket_arn]
  }
}

/*
Example: Create an User group

- User group does not support tags and will be ignored
*/

resource "aws_iam_group" "group" {
  name = "example_group_1"
  path = "/"
}