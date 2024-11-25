FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update -y && apt-get upgrade -y && \
    apt-get install -y wget mediainfo python3 python3-pip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /usr/src/app

# Copy requirements.txt
COPY requirements.txt .

# Install Python dependencies from requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Make start.sh executable
RUN chmod +x start.sh

# Start the bot
CMD ["bash", "start.sh"]
