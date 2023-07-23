resource "google_cloud_run_v2_job" "extract" {
  name     = "extract"
  location = var.region

  template {
    template {
      containers {
        image = format(
          "%s-docker.pkg.dev/%s/%s/extract@%s",
          var.region, var.project_id, var.docker_repo_id, var.extract_image_digest
        )
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
      }
      service_account = google_service_account.etl.email
    }
  }

  lifecycle {
    ignore_changes = [
      launch_stage,
    ]
  }

  depends_on = [resource.google_project_iam_member.cloud_run_developer]
}

resource "google_cloud_run_v2_job" "transform" {
  name     = "transform"
  location = var.region

  template {
    template {
      containers {
        image = format(
          "%s-docker.pkg.dev/%s/%s/transform@%s",
          var.region, var.project_id, var.docker_repo_id, var.transform_image_digest
        )
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
      }
      service_account = google_service_account.etl.email
    }
  }

  lifecycle {
    ignore_changes = [
      launch_stage,
    ]
  }

  depends_on = [resource.google_project_iam_member.cloud_run_developer]
}

resource "google_cloud_run_v2_job" "load" {
  name     = "load"
  location = var.region

  template {
    template {
      containers {
        image = format(
          "%s-docker.pkg.dev/%s/%s/load@%s",
          var.region, var.project_id, var.docker_repo_id, var.load_image_digest
        )
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
      }
      service_account = google_service_account.etl.email
    }
  }

  lifecycle {
    ignore_changes = [
      launch_stage,
    ]
  }

  depends_on = [resource.google_project_iam_member.cloud_run_developer]
}
