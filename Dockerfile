FROM python:3.8

RUN set -eux \
  &&  pip install fastapi uvicorn jinja2 requests

WORKDIR /app


CMD ["uvicorn", "spotify.app:app", "--reload", "--host", "0.0.0.0"]