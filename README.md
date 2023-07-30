# University Subreddits

!["Dashboard"](images/dashboard.png)

The r/nus subreddit is a *peculiar* place. Most people think it is toxic and predominantly negative. It got me thinking — how does r/nus stack up against other university subreddits around the world?

This dashboard uses language algorithms to gauge the sentiment of posts, and aggregates the daily upvote ratio of each university's subreddit. Feel free to use it to compare your university to any rival institutions you so desire. Suprisingly, NUS stacks up well compared to the rest of the world.

Interestingly, this project also yields a world ranking of universities based on online student satisfaction — a happiness ranking. I'll leave it's interpretation as an exercise to the reader.

# Architecture

!["Architecture"](images/architecture.png)

All infrastructure is hosted on Google Cloud Platform and managed via Terraform.

- ETL scripts are Python 3.11 docker containers running on Cloud Run Jobs. All jobs are idempotent. 

- Cloud Storage for the raw and transformed data

- BigQuery for the analytics database
  
- Cloud Scheduler to trigger the extract job at set intervals.

- EventArc + Workflows to trigger transform/load jobs upon ingestion of raw/transformed data respectively. 
