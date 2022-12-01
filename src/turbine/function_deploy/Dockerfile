# Build Data App
FROM python:3.11.0-slim as DATA_APP_BUILDER

RUN pip install --upgrade pip

RUN apt-get -y update
RUN apt-get -y install git gcc

WORKDIR /app/data_app
COPY ./data_app/requirements.txt requirements.txt
RUN pip install --requirement requirements.txt
COPY ./data_app .

# Build Function App
WORKDIR /app/function_app
COPY ./function_app/requirements.txt requirements.txt
RUN pip install --requirement requirements.txt
COPY ./function_app .

#Set user permissions to nonroot
USER nobody

ENTRYPOINT [ "python", "function_server.py" ]
