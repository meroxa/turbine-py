# Build Data App
FROM python:slim-buster as DATA_APP_BUILDER
WORKDIR /app/data-app
COPY ./data-app/requirements.txt requirements.txt
RUN pip install --requirement requirements.txt
COPY ./data-app .

# Build Function APp
FROM python:slim-buster as FUNCTION_APP_BUILDER
WORKDIR /app/function-app
COPY ./function-app/requirements.txt requirements.txt
RUN pip install --requirement requirements.txt
COPY ./function-app .

# TODO Build both things if needed
FROM python:slim-buster as APP_BUILDER
WORKDIR /app/data-app
COPY --from=DATA_APP_BUILDER ./app/data-app .
WORKDIR /app/function-app
COPY --from=FUNCTION_APP_BUILDER ./app/function-app .

CMD [ "python", "main.py" ]