FROM python:3-alpine

EXPOSE 5000

RUN apk add --update \
    build-base \
    postgresql-dev \
    libffi-dev \
    && rm -rf /var/cache/apk/*
COPY requirements.txt /src/requirements.txt
RUN ["pip", "install", "-r", "/src/requirements.txt"]

COPY health.py /health.py
HEALTHCHECK --interval=5s --timeout=1s --retries=3 CMD python /health.py localhost:5000

COPY src /src

ENV LOG_STYLE=json
ENV LOG_LEVEL=INFO

ENTRYPOINT [ "/usr/local/bin/python", "/src" ]
