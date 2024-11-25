FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Install required dependencies
RUN apt-get update -y && apt-get install -y \
    python3 \
    python3-pip \
    wget \
    mediainfo \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /usr/src/app

# Install Python packages from requirements.txt
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy the project files
COPY . .

# Set the correct file permissions
RUN chmod +x bot.py

# Start the bot using the correct command
CMD ["python3", "bot.py"]
