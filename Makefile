# ----------------------------------
#          INSTALL & TEST
# ----------------------------------
install_requirements:
	@pip install -r requirements.txt

check_code:
	@flake8 scripts/* water_pollution/*.py

black:
	@black scripts/* water_pollution/*.py

test:
	@coverage run -m pytest tests/*.py
	@coverage report -m --omit="${VIRTUAL_ENV}/lib/python*"

ftest:
	@Write me

clean:
	@rm -f */version.txt
	@rm -f .coverage
	@rm -fr */__pycache__ */*.pyc __pycache__
	@rm -fr build dist
	@rm -fr water_pollution-*.dist-info
	@rm -fr water_pollution.egg-info

install:
	@pip install . -U

all: clean install test black check_code

count_lines:
	@find ./ -name '*.py' -exec  wc -l {} \; | sort -n| awk \
        '{printf "%4s %s\n", $$1, $$2}{s+=$$0}END{print s}'
	@echo ''
	@find ./scripts -name '*-*' -exec  wc -l {} \; | sort -n| awk \
		        '{printf "%4s %s\n", $$1, $$2}{s+=$$0}END{print s}'
	@echo ''
	@find ./tests -name '*.py' -exec  wc -l {} \; | sort -n| awk \
        '{printf "%4s %s\n", $$1, $$2}{s+=$$0}END{print s}'
	@echo ''

# ----------------------------------
#      UPLOAD PACKAGE TO PYPI
# ----------------------------------
PYPI_USERNAME=<AUTHOR>
build:
	@python setup.py sdist bdist_wheel

pypi_test:
	@twine upload -r testpypi dist/* -u $(PYPI_USERNAME)

pypi:
	@twine upload dist/* -u $(PYPI_USERNAME)

# ----------------------------------
#     DOCKER / GCP
# ----------------------------------

GCP_PRJ_ID="wagon-water-backend"
DOCKER_IMG="api"
GCR_MULTI_REGION="eu.gcr.io"
GCR_REGION="europe-west1"

API_IMG="${GCR_MULTI_REGION}/${GCP_PRJ_ID}/${DOCKER_IMG}"

docker_build:
	@docker build -t ${API_IMG} .

docker_push:
	@docker push ${API_IMG}

gcr_deploy:
	@gcloud run deploy --image ${API_IMG} --platform managed --region ${GCR_REGION}
