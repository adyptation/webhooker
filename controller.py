"""
Flask controller that sets up the routes and creates the app.
"""
import os
import re
import json
import inspect
from flask import Flask, request, make_response

from handlers.handler import Handler


def controller(app):
    """
    Flask controller to setup routes and validators.
    """

    @app.before_request
    def validate_request():
        """
        Prior to any response, ensure the presented API key is
        valid.

        We will accept:
            Private x-adypta secret key (internal use only)
            Public x-api-key generated per user.
        """

        # Root URL normally provide a friendly response redirecting to docs
        # so we do not need to authenticate requests to this path
        if re.search("^/$", request.path):
            return Handler().unauthorized()

        """
        This is an old example of how we handled some adhoc auth.

        if request.headers.get("x-adypta") != os.environ.get(
            "ADYPTA_SECRET", Handler.create_random_string()
        ):
            # Invalid private secret, bail out.
            return Handler().unauthorized()
        """

    @app.route("/7cbPiUCZi", methods=["POST", "GET"])
    def malwarebytes():
        """
        Handle our malwarebytes route.

        It's a POST only route so handle others appropriately.
        """
        if request.method == "GET":
            return Handler().unauthorized()

        try:
            return Handler("malwarebytes").run()
        except Exception as e:
            msg = inspect.stack()[0][3] + " " + str(e)
            return make_response(
                json.dumps({"error": str(msg)}),
                500,
                {"Content-Type": "application/json"},
            )


def create_app(config=None):
    """
    One stop shop to bootstrap our Flask app.

    Args:
        config(dict) - optional flask configuration

    Return:
        Flask app object
    """
    app = Flask(__name__)
    app.config.from_object(config)
    controller(app)
    return app
