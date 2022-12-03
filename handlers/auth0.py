"""
Handle incoming webhooks from Auth0 for Signup Success messages.
"""
import os
from flask import request

from .handler import Handler


class Auth0(Handler):
    """
    Handler for Auth0 webhooks.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def validate_signature(self, request):
        if not request.headers.get("Authorization"):
            return False

        provided_string = request.headers.get("Authorization").split(" ")[1]

        os.environ["AUTH0_AUTHORIZATION"] = "903ATvgLIFAWQLOuSE76i9pGKI1jvD7z"

        valid_string = os.environ.get(
            "AUTH0_AUTHORIZATION", Handler.create_random_string()
        )

        return provided_string == valid_string

    def format(self, payload):
        """
        Format a Slack message based on specific payload data.

        Args:
            payload(dict) - dict of information to be formatted

        Return:
            dict - formatted object
        """
        print(payload)
        if not payload.get("data"):
            return {}

        pd = payload["data"]
        payload_type = "Login Success." if pd["type"] == "s" else pd["description"]

        message = {
            "text": f"Auth0: {payload_type}",
            "blocks": [
                # {
                #     "type": "header",
                #     "text": {
                #         "type": "plain_text",
                #         "text": f"Auth0: {payload_type}",
                #     },
                # },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": (
                            f"*Auth0*: - {pd['user_name']} {payload_type}\n"
                            f"On _{pd['client_name']}_ via _{pd['connection']}_ "
                            f"at {pd['date']}"
                        ),
                    },
                },
            ],
        }
        return message

    def debug(self, **kwargs):
        print(f"kwargs: {str(kwargs)}")
        print(request.json)
        for item in request.json:
            description = "Login Success"
            if item["data"]["type"] == "fp":
                description = item["data"]["description"]

            if item["data"]["type"] == "f":
                print(
                    f'FAILURE: {item["data"]["connection"]} - {item["data"]["description"]}'
                )
                return request.json

            print(
                "{} ({}) {}".format(
                    item["data"]["user_name"], item["data"]["user_id"], description
                )
            )

        return request.json
