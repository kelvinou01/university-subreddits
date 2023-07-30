define get_image_uri
asia-southeast1-docker.pkg.dev/university-subreddits/etl-images/$(1):latest
endef

define get_image_digest
gcloud artifacts docker images describe $(call get_image_uri,$(1)) --format="value(image_summary.digest)"
endef


pre-commit:
	pre-commit run --all-files

auth:
	gcloud auth login
	gcloud config set project university-subreddits
	gcloud auth print-access-token | docker login -u oauth2accesstoken --password-stdin https://asia-southeast1-docker.pkg.dev

test: pre-commit
	cd tests && export REDDIT_CLIENT_ID="" REDDIT_CLIENT_SECRET="" SUBREDDITS="" HUGGINGFACE_TOKEN="" && python3 -m pytest -v

first-time-setup:
	gcloud artifacts repositories create etl-images --location=asia-southeast1 --repository-format=docker
	cd terraform && terraform init

deploy-extract: pre-commit
	$(MAKE) auth
	docker buildx build --platform linux/amd64,linux/arm64 -t $(call get_image_uri,extract) -f dockerfiles/Dockerfile.extract --push .
	docker pull $(call get_image_uri,extract)
	$(MAKE) deploy-terraform

deploy-transform: pre-commit
	$(MAKE) auth
	docker buildx build --platform linux/amd64,linux/arm64 -t $(call get_image_uri,transform) -f dockerfiles/Dockerfile.transform --push .
	docker pull $(call get_image_uri,transform)
	$(MAKE) deploy-terraform

deploy-load: pre-commit
	$(MAKE) auth
	docker buildx build --platform linux/amd64,linux/arm64 -t $(call get_image_uri,load) -f dockerfiles/Dockerfile.load --push .
	docker pull $(call get_image_uri,load)
	$(MAKE) deploy-terraform

deploy-terraform: pre-commit
	export TF_VAR_extract_image_digest=$$($(call get_image_digest,extract)) && \
	export TF_VAR_transform_image_digest=$$($(call get_image_digest,transform)) && \
	export TF_VAR_load_image_digest=$$($(call get_image_digest,load)) && \
	cd terraform && terraform apply --auto-approve

local-run-extract: pre-commit
	docker run \
   		-e GOOGLE_APPLICATION_CREDENTIALS=google_application_credentials.json \
   		-v "$(shell pwd)/google_application_credentials.json":/app/google_application_credentials.json -t \
   		asia-southeast1-docker.pkg.dev/university-subreddits/etl-images/extract:latest

local-run-transform: pre-commit
	docker run \
   		-e GOOGLE_APPLICATION_CREDENTIALS=google_application_credentials.json \
   		-v "$(shell pwd)/google_application_credentials.json":/app/google_application_credentials.json -t \
   		asia-southeast1-docker.pkg.dev/university-subreddits/etl-images/extract:latest

local-run-load: pre-commit
	docker run \
   		-e GOOGLE_APPLICATION_CREDENTIALS=google_application_credentials.json \
   		-v "$(shell pwd)/google_application_credentials.json":/app/google_application_credentials.json -t \
   		asia-southeast1-docker.pkg.dev/university-subreddits/etl-images/extract:latest
