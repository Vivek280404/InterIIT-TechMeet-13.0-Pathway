# Use the base Image for Ubuntu 22.04
FROM ubuntu:22.04

# Set build arguments
ARG USER=pathway_pipeline
ARG DEBIAN_FRONTEND=noninteractive

RUN groupadd -r ${USER} && useradd -r -g ${USER} ${USER} && \
    mkdir -p /home/${USER} && \
    touch /home/${USER}/.bashrc

# Set the working directory
WORKDIR /home/${USER}

# Install necessary dependencies and Python 3.12
RUN apt-get update && \
    apt-get install -y \
    software-properties-common \
    curl \ 
    nano \  
    sudo \ 
    build-essential && \ 
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \ 
    apt-get install -y python3.12 python3-pip && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1

# Copy the required Files
COPY pipeline /home/${USER}/pipeline
COPY .env /home/${USER}/.env

# Change the Ownership of Home of the User
RUN chown -R ${USER}:${USER} /home/${USER}

# Switch to the specified User
USER ${USER}

# Install python dependencies
RUN pip install -r /home/${USER}/pipeline/requirements.txt