resource "google_bigquery_dataset" "subreddit_metrics" {
  dataset_id                  = "subreddit_metrics"
  friendly_name               = "Subreddit Metrics"
  description                 = "Main dataset for the University Subreddits project"
  location                    = var.region

  labels = {
    env = "default"
  }

  access {
    role = "OWNER"
    special_group = "projectOwners"
  }

  access {
    role = "OWNER"
    user_by_email = google_service_account.etl.email
  }
}

resource "google_bigquery_table" "subreddit_metrics" {
  dataset_id = google_bigquery_dataset.subreddit_metrics.dataset_id
  table_id   = "subreddit_metrics"

  labels = {
    env = "default"
  }

  clustering = ["date"]
  schema = <<-EOF
  [
    {
      "name": "date",
      "type": "DATE",
      "mode": "NULLABLE"
    },
    {
      "name": "subreddit",
      "type": "STRING",
      "mode": "NULLABLE"
    },
    {
      "name": "upvotes",
      "type": "INTEGER",
      "mode": "NULLABLE"
    },
    {
      "name": "downvotes",
      "type": "INTEGER",
      "mode": "NULLABLE"
    },
    {
      "name": "upvote_ratio",
      "type": "FLOAT",
      "mode": "NULLABLE"
    },
    {
      "name": "posts",
      "type": "INTEGER",
      "mode": "NULLABLE"
    },
    {
      "name": "transformed_utc",
      "type": "TIMESTAMP",
      "mode": "NULLABLE"
    },
    {
      "name": "sentiment_score",
      "type": "FLOAT",
      "mode": "NULLABLE"
    },
    {
      "name": "topics",
      "type": "STRING",
      "mode": "REPEATED"
    }
]
EOF
  
  depends_on = [google_project_iam_member.bigquery_data_owner]
}
