FROM python:3.8

WORKDIR /app

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

COPY . .

CMD ["uvicorn", "spotify.app:app", "--host", "0.0.0.0"]
