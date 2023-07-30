variable "project_id" {
  default = "university-subreddits"
}

variable "docker_repo_id" {
  default = "etl-images"
}

variable "region" {
  default = "asia-southeast1"
}

variable "credentials" {
  default = "../google_application_credentials.json"
}

variable "raw_data_prefix" {
  default = "reddit-posts/"
}

variable "transformed_data_prefix" {
  default = "subreddit-metrics/"
}

variable "extract_image_digest" {
  type = string
}

variable "transform_image_digest" {
  type = string
}

variable "load_image_digest" {
  type = string
}

variable "reddit_client_id" {
  type    = string
}

variable "reddit_client_secret" {
  type    = string
}

variable "huggingface_token" {
  type    = string
}

variable "subreddits" {
  default = "nus,ntu,sit_singapore,smu_singapore,oxforduni,harvard,cambridge_uni,stanford,mit,berkeley,ucla,ethz,uchicago,uiuc,uwaterloo,aggies,gatech,uoft,uofm,nyu,ubc"
}
