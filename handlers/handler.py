import os
import json
import time
import random
import string
import requests
import importlib
from flask import request, make_response


class Handler(object):
    module_name = None
    module = None
    mod = None

    headers = {"Content-Type": "application/json"}

    def __init__(self, module_name="malwarebytes"):
        self.module_name = module_name.title()

        if self.module_name is not None:
            mod = importlib.import_module(f"handlers.{self.module_name.lower()}")
            self.module = getattr(mod, self.module_name)

    def unauthorized(self):
        return make_response(json.dumps({"error": "Unauthorized."}), 401, self.headers)

    def invalid_data(self):
        return make_response(
            json.dumps({"error": "Invalid data received."}), 400, self.headers
        )

    def misconfiguration(self):
        return make_response(
            json.dumps({"error": "Misconfiguration."}), 500, self.headers
        )

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
        if channel == "security":
            url = os.environ.get("SLACK_CHANNEL_SECURITY")
        else:
            url = os.environ.get("SLACK_CHANNEL_DEVOPS", None)

        if url is None:
            return self.misconfiguration()

        response = requests.post(url, json.dumps(message))
        return make_response(json.dumps({"status": response.text}), 200, self.headers)

    def format(self, data):
        return self.module().format(data)

    def run(self):
        message = self.format(request.json)
        return self.send_to_slack("security", message)
