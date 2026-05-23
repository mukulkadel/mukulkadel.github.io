---
layout: post
title: "Terraform Basics: Infrastructure as Code in 10 Minutes"
date: "2026-05-23 00:00:00 +0530"
slug: terraform-basics-infrastructure-as-code
description: "Get started with Terraform by learning how to define, plan, and apply cloud infrastructure as code, with an AWS EC2 instance as a working example."
categories: ["Tutorials", "Programming"]
tags: ["terraform", "infrastructure as code", "devops", "aws", "cloud", "hcl", "iac", "automation", "tutorial"]
---

Clicking through a cloud console to provision servers is fine once. Do it a second time and you'll get something slightly different. Do it across environments and you'll spend hours debugging why staging doesn't match production. Terraform solves this by letting you describe your infrastructure in code, version it in git, and apply it repeatably. This guide covers the core workflow with a concrete AWS example.

## How Terraform Works

Terraform reads `.tf` files written in **HCL** (HashiCorp Configuration Language), figures out what resources need to be created, modified, or destroyed, and then applies those changes through provider APIs.

The workflow is always three steps:

```
terraform init → terraform plan → terraform apply
```

- **init**: downloads the required provider plugins
- **plan**: shows what will change without touching anything
- **apply**: executes the changes

## Installing Terraform

```bash
# macOS
$ brew install terraform

# verify
$ terraform version
Terraform v1.9.0
on darwin_arm64
```

## A Working Example: EC2 Instance on AWS

Create a directory and a `main.tf` file:

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "ap-south-1"
}

resource "aws_instance" "web" {
  ami           = "ami-0f58b397bc5c1f2e8"  # Amazon Linux 2023, ap-south-1
  instance_type = "t3.micro"

  tags = {
    Name        = "web-server"
    Environment = "dev"
  }
}

output "instance_ip" {
  value = aws_instance.web.public_ip
}
```

Initialize, plan, and apply:

```bash
$ terraform init
Initializing provider plugins...
- Finding hashicorp/aws versions matching "~> 5.0"...
- Installing hashicorp/aws v5.55.0...
Terraform has been successfully initialized!

$ terraform plan
Terraform will perform the following actions:

  # aws_instance.web will be created
  + resource "aws_instance" "web" {
      + ami           = "ami-0f58b397bc5c1f2e8"
      + instance_type = "t3.micro"
      + tags          = { "Environment" = "dev", "Name" = "web-server" }
      ...
    }

Plan: 1 to add, 0 to change, 0 to destroy.

$ terraform apply
Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes

aws_instance.web: Creating...
aws_instance.web: Still creating... [10s elapsed]
aws_instance.web: Creation complete after 32s [id=i-0abc123def456789]

Apply complete! Resources: 1 added, 0 changed, 0 destroyed.

Outputs:

instance_ip = "13.232.45.67"
```

## State: How Terraform Tracks Reality

After `apply`, Terraform writes a `terraform.tfstate` file that maps your HCL resources to real cloud resource IDs. On the next `plan` or `apply`, Terraform diffs your config against this state to determine what needs to change.

**Do not manually edit `terraform.tfstate`.** For teams, store state remotely so everyone shares the same view:

```hcl
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "prod/main.tfstate"
    region         = "ap-south-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
```

The DynamoDB table provides state locking — prevents two people from running `apply` simultaneously and corrupting state.

## Variables and Outputs

Hardcoding region and instance type makes configs inflexible. Extract them:

```hcl
variable "region" {
  type    = string
  default = "ap-south-1"
}

variable "instance_type" {
  type    = string
  default = "t3.micro"
}

provider "aws" {
  region = var.region
}

resource "aws_instance" "web" {
  ami           = "ami-0f58b397bc5c1f2e8"
  instance_type = var.instance_type
}
```

Override at apply time:

```bash
$ terraform apply -var="instance_type=t3.small"

# or via a tfvars file
$ terraform apply -var-file="production.tfvars"
```

## Destroying Infrastructure

```bash
$ terraform destroy
Plan: 0 to add, 0 to change, 1 to destroy.

Do you really want to destroy all resources?
  Enter a value: yes

aws_instance.web: Destroying...
aws_instance.web: Destruction complete after 40s
```

Always review the destroy plan carefully — there's no undo for cloud resources.

## Modules: Reusable Blocks

A **module** is a directory of `.tf` files that encapsulates a logical unit. Instead of repeating the same VPC, subnet, and security group config in every project, you write it once as a module:

```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"

  name = "main-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["ap-south-1a", "ap-south-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]
}
```

The [Terraform Registry](https://registry.terraform.io) has community modules for almost every AWS, GCP, and Azure resource pattern.

## Conclusion

Terraform's plan-then-apply workflow makes infrastructure changes as reviewable and predictable as code changes. The state file is the source of truth for what's deployed, remote backends keep teams in sync, and modules let you build reusable components rather than copy-pasting resource blocks across projects. Start by Terraforming one piece of your infrastructure — a single server or an S3 bucket — and you'll quickly find it easier to let Terraform manage everything than to mix manual and automated provisioning.
