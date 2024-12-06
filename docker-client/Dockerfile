# Use the official Debian image as the base
FROM debian:latest

# Set environment variables
#ENV DEBIAN_FRONTEND=noninteractive

# Copy the ttyd binary into the image
COPY ttyd.x86_64 /usr/local/bin/ttyd
#COPY tt++ /usr/local/bin/tt++

# Ensure the ttyd binary is executable
RUN chmod +x /usr/local/bin/ttyd
#RUN chmod +x /usr/local/bin/tt++

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    libssl-dev \
    libwebsockets-dev \
    libjson-c-dev \
    tintin++ \
    bash \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Expose the default ttyd port
EXPOSE 8080

# Define the entrypoint and default command
CMD ["ttyd", "-p 8080", "--writable", "/usr/games/tt++",
"-e \"#DELAY {1} {#SPLIT 0 0};\" -e \"#SESSION {3k} {127.0.0.1} {4001};\" -e \"#DELAY {1} {#SPLIT 0 0};\"]