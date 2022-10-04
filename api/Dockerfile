FROM python:3.10.7-alpine3.15

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app

RUN apk add --no-cache --virtual .build-deps gcc musl-dev ; \
    pip install -r requirements.txt ; \
    apk del .build-deps gcc musl-dev ; \
    rm -f /var/cache/apk/*

COPY . /app/

EXPOSE 5000
