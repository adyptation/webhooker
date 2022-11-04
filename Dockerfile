# Define function directory
ARG FUNCTION_DIR="/function"

FROM python:3.11-alpine AS python-alpine 
RUN apk add --no-cache \
    libstdc++

FROM python-alpine as build-image

# Install aws-lambda-cpp build dependencies
RUN apk add --no-cache \
    build-base \
    libtool \ 
    autoconf \ 
    automake \ 
    libexecinfo-dev \ 
    make \
    cmake \ 
    libcurl

# Include global arg in this stage of the build
ARG FUNCTION_DIR
# Create function directory
RUN mkdir -p ${FUNCTION_DIR}

# Install the runtime interface client
RUN python -m pip install --upgrade pip
RUN python -m pip install --target ${FUNCTION_DIR} awslambdaric

# Copy function code
COPY *.py ${FUNCTION_DIR}/
COPY handlers/*.py ${FUNCTION_DIR}/handlers/
COPY requirements.txt .

RUN python -m pip install --no-cache -r requirements.txt --target "${FUNCTION_DIR}"

# Multi-stage build: grab a fresh copy of the base image
FROM python-alpine

# Include global arg in this stage of the build
ARG FUNCTION_DIR
# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}

# Copy in the build image dependencies
COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}

ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
CMD [ "app.handler" ]