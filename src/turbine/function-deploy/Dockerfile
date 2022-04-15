# Build Data App
FROM python:slim-buster as DATA_APP_BUILDER
WORKDIR /app/data-app
COPY ./data-app/requirements.txt requirements.txt
RUN pip install --requirement requirements.txt
COPY ./data-app .

# Build Function App
#FROM python:slim-buster as FUNCTION_APP_BUILDER
WORKDIR /app/function-app
COPY ./function-app/requirements.txt requirements.txt
RUN pip install --requirement requirements.txt
COPY ./function-app .

CMD [ "python", "main.py" ]