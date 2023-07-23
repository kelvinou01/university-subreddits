
# Ref: https://cloud.google.com/workflows/docs/tutorials/execute-cloud-run-jobs
resource "google_workflows_workflow" "run_next_job" {
  name            = "run_next_job"
  region          = var.region
  description     = "Run a Transform job if raw data is uploaded, or a Load job if transformed data is uploaded"
  service_account = google_service_account.etl.email
  source_contents = <<-EOF
    main:
      params: [event]
      steps:
          - init:
              assign:
                  - project_id: ${var.project_id}
                  - event_bucket: $${event.data.bucket}
                  - event_object: $${event.data.name}
                  - target_bucket: ${google_storage_bucket.etl_bucket.name}
                  - raw_data_prefix: ${var.raw_data_prefix}
                  - transformed_data_prefix: ${var.transformed_data_prefix}
                  - transform_job_name: ${google_cloud_run_v2_job.transform.name}
                  - load_job_name: ${google_cloud_run_v2_job.load.name}
                  - job_location: ${var.region}
          - log:
              call: sys.log
              args:
                  text: '$${"run_next_job workflow called upon creation of " + event_object}'
                  severity: INFO
          - check_input_object:
              switch:
                  - condition: '$${text.match_regex(event_object, "^" + raw_data_prefix)}'
                    next: run_transform
                  - condition: '$${text.match_regex(event_object, "^" + transformed_data_prefix)}'
                    next: run_load
                  - condition: true
                    next: end
          - run_transform:
              call: googleapis.run.v1.namespaces.jobs.run
              args:
                  name: $${"namespaces/" + project_id + "/jobs/" + transform_job_name}
                  location: $${job_location}
              result: job_execution
              next: finish
          - run_load:
              call: googleapis.run.v1.namespaces.jobs.run
              args:
                  name: $${"namespaces/" + project_id + "/jobs/" + load_job_name}
                  location: $${job_location}
              result: job_execution
              next: finish
          - finish:
              return: $${job_execution}
EOF
}
