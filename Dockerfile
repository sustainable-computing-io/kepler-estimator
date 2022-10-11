FROM quay.io/sustainable_computing_io/kepler-estimator-base:latest

WORKDIR /usr/src/app
COPY src src

CMD ["python", "src/estimator.py"]