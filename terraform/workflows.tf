
# Ref: https://cloud.google.com/workflows/docs/tutorials/execute-cloud-run-jobs
resource "google_workflows_workflow" "run_next_job" {
  name            = "run_next_job"
  region          = var.region
  description     = "Run a Transform job if raw data is uploaded, or a Load job if transformed data is uploaded"
  service_account = google_service_account.etl.email
  source_contents = <<-EOF

    # Helper subworkflow to run gcloud cli commands
    # To overcome some limitations in the Cloud Run connector
    gcloud:
      params: [args]
      steps:
      - create_build:
          call: googleapis.cloudbuild.v1.projects.builds.create
          args:
            projectId: "university-subreddits"
            parent: "projects/university-subreddits/locations/global"
            body:
              serviceAccount: ${google_service_account.etl.name}
              options:
                logging: CLOUD_LOGGING_ONLY
              steps:
              - name: gcr.io/google.com/cloudsdktool/cloud-sdk
                entrypoint: /bin/bash
                args: '$${["-c", "gcloud " + args + " > $$BUILDER_OUTPUT/output"]}'
          result: result_builds_create
      - return_gcloud_result:
          return: $${text.split(text.decode(base64.decode(result_builds_create.metadata.build.results.buildStepOutputs[0])), "\n")}

    run_transform:
      params: [date]
      steps:
        - load_date_to_job_env:
            call: gcloud
            args:
                args: $${"run jobs update transform --region ${var.region} --update-env-vars DATE_TO_PROCESS=" + date}
        - run_job:
            call: googleapis.run.v1.namespaces.jobs.run
            args:
                name: $${"namespaces/${var.project_id}/jobs/${google_cloud_run_v2_job.transform.name}"}
                location: ${var.region}
            result: job_execution

    run_load:
      params: [date]
      steps:
        - load_date_to_job_env:
            call: gcloud
            args:
                args: $${"run jobs update load --region ${var.region} --update-env-vars DATE_TO_PROCESS=" + date}
        - run_job:
            call: googleapis.run.v1.namespaces.jobs.run
            args:
                name: $${"namespaces/${var.project_id}/jobs/${google_cloud_run_v2_job.transform.name}"}
                location: ${var.region}
            result: job_execution

    # some-prefix/year=2023/month=07/day=28.json -> 28/07/2023
    parse_blob_name_to_date:
      params: [blob_name]
      steps:
        - extract:
            assign:
            - year_index: $${text.find_all(blob_name, "year")[0] + 5}
            - month_index: $${text.find_all(blob_name, "month")[0] + 6}
            - day_index: $${text.find_all(blob_name, "day")[0] + 4}
            - year:  $${text.substring(blob_name, year_index, year_index + 4)}
            - month:  $${text.substring(blob_name, month_index, month_index + 2)}
            - day:  $${text.substring(blob_name, day_index, day_index + 2)}
        - return:
            return: $${day + "/" + month + "/" + year}

    main:
      params: [event]
      steps:
          - init:
              assign:
                  - blob_name: $${event.data.name}
          - log:
              call: sys.log
              args:
                  text: '$${"run_next_job workflow called upon creation of " + blob_name}'
                  severity: INFO
          - extract_date:
              call: parse_blob_name_to_date
              args:
                  blob_name: $${blob_name}
              result: date
          - check_blob_name_and_run_job:
              switch:
                  - condition: '$${text.match_regex(blob_name, "^${var.raw_data_prefix}")}'
                    call: run_transform
                    args:
                        date: $${date}
                  - condition: '$${text.match_regex(blob_name, "^${var.transformed_data_prefix}")}'
                    call: run_load
                    args:
                        date: $${date}
EOF
}
