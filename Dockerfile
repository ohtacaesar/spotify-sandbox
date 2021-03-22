FROM python:3.8

WORKDIR /app

COPY setup.py ./
COPY setup.cfg ./
COPY spotify ./spotify

RUN python ./setup.py install

COPY secret.json ./

CMD ["uvicorn", "spotify.app:app", "--host", "0.0.0.0"]
