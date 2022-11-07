# Build Data App
FROM python:3.11.0-slim as DATA_APP_BUILDER

RUN pip install --upgrade pip

RUN apt-get -y update
RUN apt-get -y install git gcc

WORKDIR /app/data-app
COPY ./data-app/requirements.txt requirements.txt
RUN pip install --requirement requirements.txt
COPY ./data-app .

# Build Function App
WORKDIR /app/function-app
COPY ./function-app/requirements.txt requirements.txt
RUN pip install --requirement requirements.txt
COPY ./function-app .

#Set user permissions to nonroot
USER nobody

ENTRYPOINT [ "python", "function_server.py" ]
