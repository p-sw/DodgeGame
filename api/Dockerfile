FROM python:3.10.7-alpine3.15

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app

RUN apk add build-base

RUN apk add --no-cache supervisor ; \
    pip install -r requirements.txt

COPY . /app/

EXPOSE 5000
