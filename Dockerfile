# Helpful AWS Guide
# https://aws.amazon.com/blogs/aws/new-for-aws-lambda-container-image-support/
# Define function directory
ARG FUNCTION_DIR="/function"
ARG RUNTIME_VERSION="3.11"
ARG DISTRO_VERSION="3.16"
ARG SERVERLESS_TAG="3.0.1"

# Stage 1 - bundle base image + runtime
FROM python:${RUNTIME_VERSION}-alpine${DISTRO_VERSION} AS python-alpine
RUN apk add --no-cache \
    libstdc++

# Stage 2 - build function and dependencies
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
    libcurl \
    git

# Include global arg in this stage of the build
ARG FUNCTION_DIR
ARG RUNTIME_VERSION
ARG SERVERLESS_TAG
# Create function directory
RUN mkdir -p ${FUNCTION_DIR}
# Install the lambda runtime interface client
RUN python -m pip install --upgrade pip
RUN python -m pip install --target ${FUNCTION_DIR} awslambdaric
# Copy function code
COPY *.py ${FUNCTION_DIR}/
COPY handlers ${FUNCTION_DIR}/handlers/
COPY requirements.txt .

RUN python -m pip install --no-cache -r requirements.txt --target "${FUNCTION_DIR}"

# Download serverless-wsgi and copy wsgi_handler.py & serverless_wsgi.py
RUN git config --global advice.detachedHead false
RUN git clone https://github.com/logandk/serverless-wsgi --branch ${SERVERLESS_TAG} ${FUNCTION_DIR}/serverless-wsgi
RUN cp ${FUNCTION_DIR}/serverless-wsgi/wsgi_handler.py ${FUNCTION_DIR}/wsgi_handler.py && cp ${FUNCTION_DIR}/serverless-wsgi/serverless_wsgi.py ${FUNCTION_DIR}/serverless_wsgi.py
RUN echo '{"app":"app.app"}' > ${FUNCTION_DIR}/.serverless-wsgi

# Stage 3 - final runtime image
FROM python-alpine
# Include global arg in this stage of the build
ARG FUNCTION_DIR
# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}
# Copy in the build image dependencies
COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}
# (Optional) Add Lambda Runtime Interface Emulator and use a script in the ENTRYPOINT for simpler local runs
ADD https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /usr/bin/aws-lambda-rie
COPY entry.sh /
RUN chmod 755 /usr/bin/aws-lambda-rie /entry.sh
EXPOSE 8080
ENTRYPOINT [ "/entry.sh" ]
# Without the Lambda Runtime Interface Emulator the entrypoint is simple and we don't need entry.sh
# ENTRYPOINT [ "/usr/local/bin/python", “-m”, “awslambdaric” ]
CMD [ "wsgi_handler.handler" ]