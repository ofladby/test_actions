#AWS_PROFILE_BRAIN_DEV should be set in the environment
#AWS_PROFILE_BRAIN_PROD should be set in the environment
#set V in CLI to change from default minor version set to the current git short hash
V ?= $(shell git rev-parse --short HEAD)
VERSION ?= $(shell date -u +%Y).$(shell date -u +%m).$(shell date -u +%d).$(V)

VERSION_FILE = .VERSION

LAMBDAS = 	testA \
			testB

LAMBDA_NAME = none
PLATFORM = manylinux2014_x86_64

S3_LAMBDA_ZIP_PATH = lambda_zips

AWS_PROFILE_BRAIN_DEV ?= Brain-DEV
S3_BUCKET_DEV = ofl-tmp-bucket

# Export all environment variables to be used in sub-makefiles
export

################################################################## DEVELOPMENT ##################################################################
# build all lambdas, exit if any build fails. At the end, update the VERSION_FILE file and commit it to git.
all: check_env
	for lambda_name in $(LAMBDAS); do \
		$(MAKE) -f makefile LAMBDA_NAME=$$lambda_name build || exit; \
	done
	$(MAKE) -f makefile update_version

login: check_env
	aws sso login --profile $(AWS_PROFILE_BRAIN_DEV)

check_env:
ifndef AWS_PROFILE_BRAIN_DEV
	$(error AWS_PROFILE_BRAIN_DEV environment variable is undefined)
endif

build: check_env
ifeq ($(LAMBDA_NAME),none)
	@echo "\nPlease override LAMBDA_NAME with the name of a lambda, use make all or make <build option>\nExamples:\n\tmake LAMBDA_NAME=dummy_lambda\n\tmake all\n"
else
	@echo "\n**************************************************\nBuilding '$(LAMBDA_NAME)' ($(VERSION))\n**************************************************\n"
	@rm -rf $(PWD)/package/*
	@mkdir -p $(PWD)/zips/$(VERSION)
	@rm -rf $(PWD)/zips/$(VERSION)/$(LAMBDA_NAME).zip
	@if [ -f $(PWD)/$(LAMBDA_NAME)/requirements.txt ]; then \
		pip install \
			--platform $(PLATFORM) \
			--target=package \
			--implementation cp \
			--python-version 3.12 \
			--only-binary=:all: --upgrade \
			-r $(PWD)/$(LAMBDA_NAME)/requirements.txt \
			-t $(PWD)/package; \
		cd $(PWD)/package && zip -r $(PWD)/zips/$(VERSION)/$(LAMBDA_NAME).zip .; \
	fi
	@if [ -f $(PWD)/$(LAMBDA_NAME)/external.py ]; then \
		cp ../../../brain/brain/external.py $(PWD)/$(LAMBDA_NAME)/external.py; \
	fi
	@if [ -d $(PWD)/$(LAMBDA_NAME)/rag/ ]; then \
		echo "Adding rag directory from '../../../rag/rag/*.py' to './rag/'"; \
		cp ../../../rag/rag/*.py $(PWD)/$(LAMBDA_NAME)/rag/; \
		rm $(PWD)/$(LAMBDA_NAME)/rag/__init__.py; \
	fi
	@if [ -d $(PWD)/$(LAMBDA_NAME)/config/ ]; then \
		echo "Adding rag config directory from '../../../rag/config/*.json' to './config/'"; \
		cp ../../../rag/config/*.json $(PWD)/$(LAMBDA_NAME)/config/; \
	fi
	@cd $(PWD)/$(LAMBDA_NAME)/ && zip -r $(PWD)/zips/$(VERSION)/$(LAMBDA_NAME).zip .
	aws s3 cp --profile $(AWS_PROFILE_BRAIN_DEV) $(PWD)/zips/$(VERSION)/$(LAMBDA_NAME).zip s3://$(S3_BUCKET_DEV)/$(S3_LAMBDA_ZIP_PATH)/$(LAMBDA_NAME).zip --metadata '{"version":"$(VERSION)","builder":"$(USER)"}'	
	@rm -rf $(PWD)/package/*
	@echo "\n**************************************************\nDONE building '$(LAMBDA_NAME)' ($(VERSION))\n**************************************************\n"
endif

update_version:
	@echo "\nStoring current version ($(VERSION)) in $(VERSION_FILE) file and commiting it to git\n"
	@git fetch --all
	@git checkout origin/dev -- $(VERSION_FILE)
	@echo $(VERSION) > $(VERSION_FILE)
	@git commit -m "Updated version to $(VERSION) for production deployment" $(VERSION_FILE)
	@git push
	@echo "\nVersion $(VERSION) stored in $(VERSION_FILE) file and committed to git\n"