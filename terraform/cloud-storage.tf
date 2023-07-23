resource "google_storage_bucket" "etl_bucket" {
  name          = "university-subreddits-etl"
  location      = var.region
  storage_class = "STANDARD"

  versioning {
    enabled = true
  }

  public_access_prevention = "enforced"
}
