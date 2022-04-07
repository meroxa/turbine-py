# Build Data App
FROM python:3-alpine3.10 as DATA_APP_BUILDER
WORKDIR /app/data-app
COPY ./data-app/requirements.txt requirements.txt
RUN pip install --requirement requirements.txt
COPY ./data-app .


# TODO Build function-app if needed

# TODO Build both things if needed

