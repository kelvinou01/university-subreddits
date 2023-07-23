# University Subreddits

!["Dashboard"](images/dashboard.png)

The r/nus subreddit is a *peculiar* place. Most people think it is toxic and predominantly negative. It got me thinking — how does r/nus stack up against other university subreddits around the world?

This dashbaoard uses language algorithms to gauge the sentiment of posts, and aggregrates the daily upvote ratio of each university's subreddit. Feel free to use it to compare your university to any rival institutions you so desire. Suprisingly, NUS stacks up well compared to the rest of the world.

Interestingly, this project also yields a world ranking of universities based on online student satisfaction — a happiness ranking.

# Architecture

!["Architecture"](images/architecture.png)

All infrastructure is hosted on Google Cloud Platform and managed via Terraform.

- Python 3.11 docker containers running on Cloud Run Jobs
  
- Cloud Storage for the raw and transformed data
  
- Google BigQuery for the analytics database
  
- Cloud Scheduler to trigger the **extract** task, and EventArc + Workflows to trigger the **transform** and **load** tasks