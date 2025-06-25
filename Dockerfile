ARG SYS_PLATFORM

FROM --platform=$SYS_PLATFORM python:3.9.10-slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# AWS specific env variables
### Set AWS_METADATA_SERVICE_TIMEOUT - set the timeout to 3 seconds
ENV AWS_METADATA_SERVICE_TIMEOUT=3
### set AWS_METADATA_SERVICE_NUM_ATTEMPTS - set the max attempts to 3
ENV AWS_METADATA_SERVICE_NUM_ATTEMPTS=3

# Args passed in the build command
ARG SERVICE_NAME

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
        git \
        gcc \
        openssh-server \
        curl \
        build-essential \
        libssl-dev \
        libffi-dev \
        python3-dev \
        pkg-config \
        procps

# Upgrade pip and install Python tools first
RUN pip install --upgrade pip setuptools wheel

# Install Rust
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Install pipenv after setuptools update
RUN pip install pipenv

# Set up SSH for private repositories
RUN mkdir -p /root/.ssh
COPY .ssh/id_rsa /root/.ssh/id_rsa
COPY .ssh/known_hosts /root/.ssh/known_hosts
RUN chmod 600 /root/.ssh/id_rsa
RUN chmod 644 /root/.ssh/known_hosts

# Add Bitbucket to known hosts and configure Git
RUN ssh-keyscan -t rsa bitbucket.org >> /root/.ssh/known_hosts
RUN git config --global core.sshCommand "ssh -o UserKnownHostsFile=/root/.ssh/known_hosts -o StrictHostKeyChecking=no -i /root/.ssh/id_rsa"

# Create app directory
RUN mkdir -p /home/ubuntu/apps/$SERVICE_NAME/logs
WORKDIR /home/ubuntu/apps/$SERVICE_NAME

RUN pip install aerich==0.7.2 premailer==3.10.0 pyjade==4.0.0 Jinja2==2.10.1 MarkupSafe==0.23 \
    sanic==22.12.0 sanic-openapi==21.12.0
# Copy requirements files
COPY Pipfile Pipfile.lock /home/ubuntu/apps/$SERVICE_NAME/
RUN pipenv sync --system

# Copy code folder
COPY . .

# Start the service
CMD ["python3", "-m", "app.service"]