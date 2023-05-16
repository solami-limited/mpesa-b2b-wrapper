FROM python:3.9.16-slim
LABEL authors="clov"

ENV CONTAINER_HOME=/var/www/mpesa-b2b-wrapper

# update apt-get and install dependencies
RUN apt-get update && apt-get -y install \
    libpq-dev \
    gcc \
    netcat && rm -rf /var/lib/apt/lists/*

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set work directory
WORKDIR $CONTAINER_HOME

# upgrade pip, install pipenv and importlib_metadata
RUN pip install --upgrade pip importlib_metadata pipenv
# install dependencies
COPY ../Pipfile* .
RUN pipenv install --system --deploy --ignore-pipfile

# copy project
COPY .. .

# Rename .env.docker file to .env
RUN mv .env.docker .env

# give permissions to entrypoint.sh
RUN chmod u+x ./.devops/entrypoint.sh

# run entrypoint.sh
ENTRYPOINT ["./.devops/entrypoint.sh"]
