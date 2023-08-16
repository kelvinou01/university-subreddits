resource "google_cloud_run_v2_service" "extract" {
  name     = "extract-${terraform.workspace}"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_INTERNAL_ONLY"

  template {
    scaling {
      min_instance_count = 0
      max_instance_count = 100
    }
    containers {
      image = format(
        "%s-docker.pkg.dev/%s/%s/extract@%s",
        var.region, var.project_id, var.docker_repo_id, var.extract_image_digest
      )
      ports {
        container_port = 80
      }
      env {
        name  = "SUBREDDITS"
        value = var.subreddits
      }
      env {
        name  = "REDDIT_CLIENT_ID"
        value = var.reddit_client_id
      }
      env {
        name  = "REDDIT_CLIENT_SECRET"
        value = var.reddit_client_secret
      }
      env {
        name  = "HUGGINGFACE_TOKEN"
        value = var.huggingface_token
      }
      env {
        name  = "GCS_RAW_BUCKET_NAME"
        value = google_storage_bucket.raw_data_bucket.name
      }
      env {
        name  = "GCS_TRANSFORMED_BUCKET_NAME"
        value = google_storage_bucket.transformed_data_bucket.name
      }
      env {
        name  = "BIGQUERY_DATASET_ID"
        value = google_bigquery_dataset.subreddit_metrics.dataset_id
      }
      env {
        name  = "BIGQUERY_TABLE_ID"
        value = google_bigquery_table.subreddit_metrics.table_id
      }
    }
    service_account = google_service_account.etl.email
  }

  lifecycle {
    ignore_changes = [
      launch_stage,
    ]
  }

  depends_on = [resource.google_project_iam_member.cloud_run_developer]
}

resource "google_cloud_run_v2_service" "transform" {
  name     = "transform-${terraform.workspace}"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_INTERNAL_ONLY"

  template {
    scaling {
      min_instance_count = 0
      max_instance_count = 100
    }
    containers {
      image = format(
        "%s-docker.pkg.dev/%s/%s/transform@%s",
        var.region, var.project_id, var.docker_repo_id, var.transform_image_digest
      )
      ports {
        container_port = 80
      }
      env {
        name  = "SUBREDDITS"
        value = var.subreddits
      }
      env {
        name  = "REDDIT_CLIENT_ID"
        value = var.reddit_client_id
      }
      env {
        name  = "REDDIT_CLIENT_SECRET"
        value = var.reddit_client_secret
      }
      env {
        name  = "HUGGINGFACE_TOKEN"
        value = var.huggingface_token
      }
      env {
        name  = "GCS_RAW_BUCKET_NAME"
        value = google_storage_bucket.raw_data_bucket.name
      }
      env {
        name  = "GCS_TRANSFORMED_BUCKET_NAME"
        value = google_storage_bucket.transformed_data_bucket.name
      }
      env {
        name  = "BIGQUERY_DATASET_ID"
        value = google_bigquery_dataset.subreddit_metrics.dataset_id
      }
      env {
        name  = "BIGQUERY_TABLE_ID"
        value = google_bigquery_table.subreddit_metrics.table_id
      }
    }
    service_account = google_service_account.etl.email
  }

  lifecycle {
    ignore_changes = [
      launch_stage,
    ]
  }

  depends_on = [resource.google_project_iam_member.cloud_run_developer]
}

resource "google_cloud_run_v2_service" "load" {
  name     = "load-${terraform.workspace}"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_INTERNAL_ONLY"

  template {
    scaling {
      min_instance_count = 0
      max_instance_count = 100
    }
    containers {
      image = format(
        "%s-docker.pkg.dev/%s/%s/load@%s",
        var.region, var.project_id, var.docker_repo_id, var.load_image_digest
      )
      ports {
        container_port = 80
      }
      env {
        name  = "SUBREDDITS"
        value = var.subreddits
      }
      env {
        name  = "REDDIT_CLIENT_ID"
        value = var.reddit_client_id
      }
      env {
        name  = "REDDIT_CLIENT_SECRET"
        value = var.reddit_client_secret
      }
      env {
        name  = "HUGGINGFACE_TOKEN"
        value = var.huggingface_token
      }
      env {
        name  = "GCS_RAW_BUCKET_NAME"
        value = google_storage_bucket.raw_data_bucket.name
      }
      env {
        name  = "GCS_TRANSFORMED_BUCKET_NAME"
        value = google_storage_bucket.transformed_data_bucket.name
      }
      env {
        name  = "BIGQUERY_DATASET_ID"
        value = google_bigquery_dataset.subreddit_metrics.dataset_id
      }
      env {
        name  = "BIGQUERY_TABLE_ID"
        value = google_bigquery_table.subreddit_metrics.table_id
      }
    }
    service_account = google_service_account.etl.email
  }

  lifecycle {
    ignore_changes = [
      launch_stage,
    ]
  }

  depends_on = [resource.google_project_iam_member.cloud_run_developer]
}
