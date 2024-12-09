#AWS_PROFILE_BRAIN_DEV should be set in the environment
#AWS_PROFILE_BRAIN_PROD should be set in the environment
#set V in CLI to change from default minor version 0
V ?= $(shell git rev-parse --short HEAD)
VERSION ?= $(shell date -u +%Y).$(shell date -u +%m).$(shell date -u +%d).$(V)

VERSION_FILE ?= .VERSION

PROD_VERSION ?= $(shell cat $(VERSION_FILE))

AWS_REGION = eu-west-2
DOCKERFILE = dockerfile

AWS_PROFILE_BRAIN_DEV ?= Brain-DEV
DEV_IMAGE = ofl-temp-dev
DEV_AWS_ACCOUNT = 891377009928
DEV_AWS_ECR = $(DEV_AWS_ACCOUNT).dkr.ecr.$(AWS_REGION).amazonaws.com
DEV_AWS_REPO = $(DEV_AWS_ECR)/$(DEV_IMAGE)

AWS_PROFILE_BRAIN_PROD ?= Brain-PROD
PROD_IMAGE = ofl-temp-prod
PROD_AWS_ACCOUNT = 891377009928
PROD_AWS_ECR = $(PROD_AWS_ACCOUNT).dkr.ecr.$(AWS_REGION).amazonaws.com
PROD_AWS_REPO = $(PROD_AWS_ECR)/$(PROD_IMAGE)


################################################################## DEVELOPMENT ##################################################################
build:	
	docker build -f $(DOCKERFILE) -t $(DEV_IMAGE):$(VERSION) . 

run: build
	docker run \
		-e ENVIRONMENT=dev \
		-e STEP_FUNCTION_ARN=arn:aws:states:eu-west-1:637423254441:stateMachine:cyberbrain_braingpt_sfn \
		-e CHAT_STEP_FUNCTION_ARN=arn:aws:states:eu-west-1:637423254441:stateMachine:cyberbrain_braingpt_chat_sfn \
		-e JWT_URL=https://cplabs-pages.cloudflareaccess.com/cdn-cgi/access/certs \
		-e JWT_ISS=https://cplabs-pages.cloudflareaccess.com \
		-e JWT_AUD=92b8b08309456a18f7f1687a9beb8b5e0a7fa7af4c175e0f243978b0ec768456 \
		-v $(HOME)/.aws/:/root/.aws/:ro \
		-v $(PWD)/code:/home/app/code/:ro \
		-v $(PWD)/data:/data/:ro \
		-it \
		-p 80:80 \
		--read-only \
		--tmpfs /tmp \
		$(DEV_IMAGE):$(VERSION)

bash:
	docker run \
		-e ENVIRONMENT=dev \
		-e STEP_FUNCTION_ARN=arn:aws:states:eu-west-1:637423254441:stateMachine:cyberbrain_braingpt_sfn \
		-e CHAT_STEP_FUNCTION_ARN=arn:aws:states:eu-west-1:637423254441:stateMachine:cyberbrain_braingpt_chat_sfn \
		-v $(HOME)/.aws/credentials:/root/.aws/credentials:ro \
		-v $(PWD)/code:/home/app/code/:ro \
		-v $(PWD)/data:/data/:ro \
		-p 80:80 \
		-it \
		--entrypoint /bin/bash \
		$(DEV_IMAGE):$(VERSION)

login_local:
	aws sso login --sso-session crosspointlabs
	aws ecr get-login-password --profile $(AWS_PROFILE_BRAIN_DEV) --region $(AWS_REGION) | docker login --username AWS --password-stdin $(DEV_AWS_ECR)

login:
	aws ecr get-login-password --profile $(AWS_PROFILE_BRAIN_DEV) --region $(AWS_REGION) | docker login --username AWS --password-stdin $(DEV_AWS_ECR)

push:
	docker tag $(DEV_IMAGE):$(VERSION) $(DEV_AWS_REPO):$(VERSION)
	docker push $(DEV_AWS_REPO):$(VERSION)

update_version:
	@echo "\nStoring current version ($(VERSION)) in $(VERSION_FILE) file and commiting it to git\n"
	@git fetch --all
	@git checkout origin/dev -- $(VERSION_FILE)
	@echo $(VERSION) > $(VERSION_FILE)
	@git commit -m "Updated version to $(VERSION) for production deployment" $(VERSION_FILE)
	@git push
	@echo "\nVersion $(VERSION) stored in $(VERSION_FILE) file and committed to git\n"


test:
	curl -X GET -IL "http://localhost:80/health/"
	curl -X GET -L "http://localhost:80/health/"

all: build push
	cd ../terraform && terraform apply -auto-approve

server:
	ngrok http 80

################################################################## PRODUCTION ##################################################################
check_prod_env:
ifndef PROD_VERSION
	$(error PROD_VERSION environment variable is undefined)
endif
	
# push_to_prod requires to set PROD_VERSION in the environment. This version should match a version already in the DEV stack ECR.
push_to_prod: check_prod_env
	@echo ""
	@echo "Pushing version $(PROD_VERSION) to prod"
	@echo ""
	@echo "Logging in to dev ECR"
	@echo ""
	@aws ecr get-login-password --profile $(AWS_PROFILE_BRAIN_DEV) --region $(AWS_REGION) | docker login --username AWS --password-stdin $(DEV_AWS_ECR)
	@echo "Pulling dev image $(DEV_AWS_REPO):$(PROD_VERSION)"	
	@echo ""
	docker pull $(DEV_AWS_REPO):$(PROD_VERSION)
	@echo "Tagging prod image $(PROD_AWS_REPO):$(PROD_VERSION)"
	@echo ""
	@docker tag $(DEV_AWS_REPO):$(PROD_VERSION) $(PROD_AWS_REPO):$(PROD_VERSION)
	@echo "Logging in to prod ECR"
	@echo ""
	@aws ecr get-login-password --profile $(AWS_PROFILE_BRAIN_PROD) --region $(AWS_REGION) | docker login --username AWS --password-stdin $(PROD_AWS_ECR)
	@echo "Pushing prod image $(PROD_AWS_REPO):$(PROD_VERSION)"
	@echo ""
	docker push $(PROD_AWS_REPO):$(PROD_VERSION)
	@echo ""
	@echo "Pushed version $(PROD_VERSION) to prod"
	@echo ""

