#AWS_PROFILE_BRAIN_DEV should be set in the environment
#AWS_PROFILE_BRAIN_PROD should be set in the environment
#set V in CLI to change from default minor version 0
V ?= 0
VERSION ?= $(shell date -u +%Y).$(shell date -u +%m).$(shell date -u +%d).$(V)

LAMBDAS = 	testB

LAMBDA_NAME = none
PLATFORM = manylinux2014_x86_64

S3_LAMBDA_ZIP_PATH = lambda_zips

AWS_PROFILE_BRAIN_DEV ?= Brain-DEV
S3_BUCKET_DEV = common-artifacts-dev-9c0baa5

################################################################## DEVELOPMENT ##################################################################
all: normal_all

normal_all:
	for lambda_name in $(LAMBDAS); do \
		$(MAKE) -f makefile LAMBDA_NAME=$$lambda_name build; \
	done

build_testB:
	$(MAKE) -f makefile LAMBDA_NAME=testB build

login: check_env
	aws sso login --profile $(AWS_PROFILE_BRAIN_DEV)

check_env:
ifndef AWS_PROFILE_BRAIN_DEV
	$(error AWS_PROFILE_BRAIN_DEV environment variable is undefined)
endif

build: check_env
ifeq ($(LAMBDA_NAME),none)
	@echo "\nPlease override LAMBDA_NAME with the name of a lambda, use make all or make <build option>\nExamples:\n\tmake LAMBDA_NAME=dummy_lambda\n\tmake all\n\tmake build_dummy_lambda\n\n"
else
	@echo "\n**************************************************\nBuilding '$(LAMBDA_NAME)' (v$(VERSION))\n**************************************************\n"
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
#	aws s3 cp --profile $(AWS_PROFILE_BRAIN_DEV) $(PWD)/zips/$(VERSION)/$(LAMBDA_NAME).zip s3://$(S3_BUCKET_DEV)/$(S3_LAMBDA_ZIP_PATH)/$(LAMBDA_NAME).zip --metadata '{"version":"$(VERSION)","builder":"$(USER)"}'	
	@rm -rf $(PWD)/package/*
	@echo "\n**************************************************\nDONE building '$(LAMBDA_NAME)' (v$(VERSION))\n**************************************************\n"
endif