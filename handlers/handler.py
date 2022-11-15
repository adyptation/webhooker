"""
Master handler class that invokes other handlers for each vendor.
"""
import os
import json
import time
import inspect
import random
import string
import requests
import importlib
from flask import request, make_response


class Handler(object):
    """
    Master handler class that invokes other handlers for each vendor.
    """

    google_project_id = "adypta-webhooker"
    module_name = None
    module = None
    mod = None

    headers = {"Content-Type": "application/json"}

    def __init__(self, module_name="malwarebytes"):
        self.module_name = module_name.title()

        if self.module_name != "":
            mod = importlib.import_module(f"handlers.{self.module_name.lower()}")
            self.module = getattr(mod, self.module_name)

    def unauthorized(self):
        return make_response(json.dumps({"error": "Unauthorized."}), 401, self.headers)

    def invalid_data(self, e=""):
        return make_response(
            json.dumps({"error": "Invalid data received.", "errorMessage": e}),
            400,
            self.headers,
        )

    def misconfiguration(self):
        return make_response(
            json.dumps({"error": "Misconfiguration."}), 500, self.headers
        )

    @staticmethod
    def get_secret(project_id, secret_id):
        """
        Get information about the given secret. This only returns metadata about
        the secret container, not any secret material.

        This process is super slow and should be avoided if possible. Using
        environment variables as a primary and this as a backup is ideal.

        Args:
            project_id(str) - The google cloud project id
            secret_id(str) - The secret to find the value of
        Returns:
            str or None - The value of the secret if defined
        """
        # Import the Secret Manager client library.
        from google.cloud import secretmanager
        from google.auth.exceptions import DefaultCredentialsError

        try:
            # Create the Secret Manager client.
            client = secretmanager.SecretManagerServiceClient()

            # Build the resource name of the secret.
            name = client.secret_path(project_id, secret_id)

            # Get the secret.
            response = client.get_secret(request={"name": name})

            # Get the replication policy.
            if "automatic" in response.replication:
                replication = "AUTOMATIC"
            elif "user_managed" in response.replication:
                replication = "MANAGED"
            else:
                raise "Unknown replication {}".format(response.replication)

            name = f"{response.name}/versions/latest"
            # Access the secret version.
            response = client.access_secret_version(request={"name": name})

            # Print the secret payload.
            #
            # WARNING: Do not print the secret in a production environment - this
            # snippet is showing how to access the secret material.
            payload = response.payload.data.decode("UTF-8")
            return payload
        except DefaultCredentialsError as dce:
            print(dce)
            return None

    @staticmethod
    def create_random_string():
        """
        Generate a random secret if no secret is set in the env.
        This prevents a gap in our private key use. Something is always set.
        It's always a value that cannot be guessed.
        """
        s = "".join(
            random.SystemRandom().choice(string.ascii_letters + string.digits)
            for _ in range(24)
        )
        val = s + str(time.time())
        return val[0:40]

    def send_to_slack(self, channel, message):
        try:
            if channel == "security":
                url = os.environ.get(
                    "SLACK_CHANNEL_SECURITY",
                    self.get_secret(self.google_project_id, "slack_channel_security"),
                )
            else:
                url = os.environ.get(
                    "SLACK_CHANNEL_DEVOPS",
                    self.get_secret(self.google_project_id, "slack_channel_devops"),
                )
        except Exception as e:
            return self.invalid_data(e)

        if url == "":
            return self.misconfiguration()

        try:
            print(f"url: {url}")
            response = requests.post(url, json.dumps(message))
            print(f"response.text: {response.text}")
            return make_response(
                json.dumps({"status": response.text}), 200, self.headers
            )
        except Exception as e:
            return make_response(
                json.dumps({"error": f"{__name__}:{inspect.stack()[0][3]}: {e}"}),
                500,
                self.headers,
            )

    def format(self, data):
        return self.module().format(data)

    def subscribe(self, **kwargs):
        print(kwargs)
        h = self.module()
        return h.subscribe(**kwargs)

    def run(self):
        try:
            message = self.format(request.json)
            print(message)
            return self.send_to_slack("security", message)
        except Exception as e:
            print(e)
            return make_response(json.dumps({"error": e}), 500, self.headers)
