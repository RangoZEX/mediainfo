FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y && apt-get install -y \
    python3 \
    python3-pip \
    wget \
    mediainfo \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

RUN chmod +x bot.py

CMD ["python3", "bot.py"]
