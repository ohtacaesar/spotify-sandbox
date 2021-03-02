FROM python:3.8

RUN set -eux \
  &&  pip install flask requests

WORKDIR /app
