terraform {
  required_version = ">= 1.8.2"

  backend "s3" {
    bucket  = "rechol-misc"
    key     = "infra/terraform/terraform.tfstate"
    region  = "us-east-1"
    profile = "rechol"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.60.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = ">= 4.0.6"
    }
  }
}

provider "aws" {
  region  = "us-east-1"
  profile = "rechol"
}
