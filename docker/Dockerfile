FROM python:alpine3.20

RUN apk update
RUN apk upgrade
RUN apk add --no-cache ffmpeg

COPY src/ /app
COPY requirements.txt /app/requirements.txt
WORKDIR /app

RUN pip install -r requirements.txt

ENV SOURCE_DIR=/source
ENV TARGET_DIR=/target
ENV TARGET_COPY_DIR=/target/copy
ENV DB_FILE=./db/music_metadata.db
ENV ALBUM_NAME=""
ENV ARTIST_NAME=""

CMD python main.py