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
