FROM quay.io/sustainable_computing_io/kepler-estimator-base:latest

WORKDIR /usr/src/app
RUN mkdir -p src
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY src src

CMD ["python", "src/estimator.py"]