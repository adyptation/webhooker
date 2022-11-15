# Webhooker

A silly name for a silly app. Webhooker is a simple exercise that:

1. Listens for incoming webhooks
1. Processes the webhook
1. Sends a formatted notification to a Slack channel

## Overview

The initial goal was to receive incoming webhooks from
Malwarebytes and send key updates to Slack to maintain
a level of central communications and visibility to the
security team.

An attempt was made to be forward thinking and process
webhooks from other vendors, but the quality there is yet
to be tested. The project is a Python Flask service designed
to be deployed to AWS Lambda by Serverless (<https://serverless.com>).

It builds out a customer container running Python 3.11 using
the Alpine distro to keep the size small.

It utilizes Github Actions to manage the builds and deploy updates
to AWS.

## Docker Notes

This project evolved to support AWS and Google Cloud so there are two
Dockerfile configurations to support each.

The containers can be built locally with something similar to the following.

### AWS

```bash
# Define AWS_ECR and AWS_REGION as environment variables
APP_NAME=webhooker-dev-app
docker build -t $APP_NAME .
docker tag $APP_NAME:latest $AWS_ECR/$APP_NAME:latest
# Login and push a copy up to AWS
aws ecr --region $AWS_REGION get-login-password | docker login --username AWS --password-stdin $AWS_ECR
docker push $AWS_ECR/$APP_NAME:latest
```

### Google Cloud

```bash
APP_NAME=gcloud-webhooker
docker build -f Dockerfile.gcloud -t $APP_NAME .
```

## Notes

One of the key learnings from this is to dynamically build and deploy
a custom container to run in the AWS Lambda environment. At the time
of this project's inception, AWS Lambda only supported up to Python 3.9
which was already in a security patch only state and Python 3.11 had
been released. AWS has been slow to update the Python versions (<https://github.com/aws/aws-lambda-base-images/issues/31>).

AWS Guide on Lambda Container support - <https://aws.amazon.com/blogs/aws/new-for-aws-lambda-container-image-support/>
Creating Containerized Flask app - <https://pritul95.github.io/blogs/aws/2020/12/25/flask-aws-containerized-lambda/>

[Steve Helms](https://github.com/stevenhelms)
_[Last updated: 2022-11-15]_
