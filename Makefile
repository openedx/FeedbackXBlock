.PHONY: docs upgrade test quality install

REPO_NAME := FeedbackXBlock
DOCKER_NAME := feedbackxblock

# For opening files in a browser. Use like: $(BROWSER)relative/path/to/file.html
BROWSER := python -m webbrowser file://$(CURDIR)/

help: ## display this help message
	@echo "Please use \`make <target>' where <target> is one of"
	@awk -F ':.*?## ' '/^[a-zA-Z]/ && NF==2 {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

install-test:
	pip install -q -r requirements/test.txt

install-dev:
	pip install -q -r requirements/dev.txt

install: install-test

quality:  ## Run the quality checks
	pycodestyle --max-line-length=120 --config=.pep8 feedback
	pylint --rcfile=pylintrc feedback
	python setup.py -q sdist
	twine check dist/*

test:  ## Run the tests
	mkdir -p var
	rm -rf .coverage
	DJANGO_SETTINGS_MODULE=feedback.settings.test python -m coverage run --rcfile=.coveragerc  -m pytest

covreport:  ## Show the coverage results
	python -m coverage report -m --skip-covered

upgrade: export CUSTOM_COMPILE_COMMAND=make upgrade
upgrade: ## update the requirements/*.txt files with the latest packages satisfying requirements/*.in
	pip install -q -r requirements/pip-tools.txt
	pip-compile --upgrade --allow-unsafe -o requirements/pip.txt requirements/pip.in
	pip-compile --upgrade -o requirements/pip-tools.txt requirements/pip-tools.in
	pip install -q -r requirements/pip.txt
	pip install -q -r requirements/pip-tools.txt
	pip-compile --upgrade -o requirements/base.txt requirements/base.in
	pip-compile --upgrade -o requirements/dev.txt requirements/dev.in
	pip-compile --upgrade -o requirements/test.txt requirements/test.in
	pip-compile --upgrade -o requirements/quality.txt requirements/quality.in
	pip-compile --upgrade -o requirements/tox.txt requirements/tox.in
	pip-compile --upgrade -o requirements/ci.txt requirements/ci.in
	pip-compile --upgrade -o requirements/docs.txt requirements/docs.in
	# lets tox controls the django versions.
	sed -i.tmp '/^[d|D]jango==/d' requirements/test.txt
	rm requirements/test.txt.tmp

requirements: ## install development environment requirements
	pip install -r requirements/pip.txt
	pip install -qr requirements/pip-tools.txt
	pip install -r requirements/dev.txt

dev.clean:
	-docker rm $(DOCKER_NAME)-dev
	-docker rmi $(DOCKER_NAME)-dev

dev.build:
	docker build -t $(DOCKER_NAME)-dev $(CURDIR)

dev.run: dev.clean dev.build ## Clean, build and run test image
	docker run -p 8000:8000 -v $(CURDIR):/usr/local/src/$(REPO_NAME) --name $(DOCKER_NAME)-dev $(DOCKER_NAME)-dev

## Localization targets

WORKING_DIR := feedback
EXTRACT_DIR := $(WORKING_DIR)/conf/locale/en/LC_MESSAGES
JS_TARGET := $(WORKING_DIR)/public/js/translations
EXTRACTED_DJANGO_PARTIAL := $(EXTRACT_DIR)/django-partial.po
EXTRACTED_DJANGOJS_PARTIAL := $(EXTRACT_DIR)/djangojs-partial.po
EXTRACTED_DJANGO := $(EXTRACT_DIR)/django.po

extract_translations: ## extract strings to be translated, outputting .po files
	cd $(WORKING_DIR) && i18n_tool extract
	mv $(EXTRACTED_DJANGO_PARTIAL) $(EXTRACTED_DJANGO)
	# Safely concatenate djangojs if it exists
	if test -f $(EXTRACTED_DJANGOJS_PARTIAL); then \
	  msgcat $(EXTRACTED_DJANGO) $(EXTRACTED_DJANGOJS_PARTIAL) -o $(EXTRACTED_DJANGO) && \
	  rm $(EXTRACTED_DJANGOJS_PARTIAL); \
	fi
	sed -i'' -e 's/nplurals=INTEGER/nplurals=2/' $(EXTRACTED_DJANGO)
	sed -i'' -e 's/plural=EXPRESSION/plural=\(n != 1\)/' $(EXTRACTED_DJANGO)

html: docs  ## An alias for the docs target.

docs: ## generate Sphinx HTML documentation, including API docs
	SPHINXOPTS="-W" make -C docs html
	$(BROWSER)docs/build/html/index.html

docs-%: ## Passthrough docs make commands
	SPHINXOPTS="-W" make -C docs $*
