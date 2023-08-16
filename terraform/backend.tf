terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.34.0"
    }
  }
  backend "gcs" {
    bucket = "university-subreddits-terraform"
    prefix = "state/"
  }
}
