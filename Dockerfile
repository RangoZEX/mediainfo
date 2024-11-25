FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y wget mediainfo
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

RUN apt-get install -y python3 python3-pip
RUN pip3 install --no-cache-dir pyrogram python-dotenv

RUN chmod +x start.sh
