resource "google_storage_bucket" "raw_data_bucket" {
  name          = "university-subreddits-raw-${terraform.workspace}"
  location      = var.region
  storage_class = "STANDARD"

  versioning {
    enabled = true
  }

  public_access_prevention = "enforced"
}

resource "google_storage_bucket" "transformed_data_bucket" {
  name          = "university-subreddits-transformed-${terraform.workspace}"
  location      = var.region
  storage_class = "STANDARD"

  versioning {
    enabled = true
  }

  public_access_prevention = "enforced"
}
