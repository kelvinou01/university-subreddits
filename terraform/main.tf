provider "google" {
  credentials = file(var.credentials)
  project     = var.project_id
  region      = var.region
}

data "google_project" "project" {}
