# Build Data App
FROM python:3.11.3-slim as DATA_APP_BUILDER
WORKDIR /app
COPY . .
RUN pip install --upgrade pip
RUN pip install -U turbine-py
RUN pip install --requirement requirements.txt

RUN apt-get -y update
RUN apt-get -y install git gcc
#Set user permissions to nonroot
USER nobody
ENTRYPOINT ["turbine-py", "serve"]
