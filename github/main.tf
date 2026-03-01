terraform {
  required_providers {
    github = {
        source = "integrations/github"
        version = ">= 4.0"}
  }
}

resource "github_repository" "repo" {
  name        = var.github_repo
  description = "Repository for Terraform state and GitHub Actions integration"
  visibility  = "public"
}

variable "github_repo" {
    description = "the name of the repo you wish to create"
}