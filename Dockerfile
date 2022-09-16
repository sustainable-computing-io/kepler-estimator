FROM python:3.8

WORKDIR /usr/src/app
RUN mkdir -p src
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY src src

CMD ["python", "src/estimator.py"]