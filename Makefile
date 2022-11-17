IMAGE_REPO :=quay.io/sustainable_computing_io/kepler-estimator
IMAGE_VERSION := "latest"

CTR_CMD :=$(or $(shell which podman 2>/dev/null), $(shell which docker 2>/dev/null))
CTR_CMD = docker
build:
	$(CTR_CMD) build -t $(IMAGE_REPO):$(IMAGE_VERSION) .

test:
	python src/estimator_test.py