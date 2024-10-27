FROM python:3.11-alpine
LABEL maintainer="adamdelezuch89@gmail.com"

ENV PYTHONUNBUFFERED 1

RUN mkdir -p /var/lib/data
RUN chmod 755 /var/lib/data

# Install system dependencies for psycopg2
RUN apk add --update --no-cache --virtual \
    .tmp-build-deps \
    build-base \
    postgresql-dev \
    musl-dev \
    zlib \
    zlib-dev \
    linux-headers 

# Install system dependencies for gdal
RUN apk add --update --no-cache \
    proj \
    proj-dev \
    proj-util \
    gcc \
    python3-dev \
    gdal-dev \
    geos-dev 

# Set PROJ_DIR environment variable
ENV PROJ_DIR=/usr

COPY ./requirements.txt /tmp/requirements.txt

RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -rf /tmp

# Copy the project files into the container
COPY ./src /app/
WORKDIR /app
