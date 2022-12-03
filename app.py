"""
Entrypoint for our Flask app.
"""
import os
import sys
from icecream import ic

from handlers.handler import Handler
from controller import create_app


"""
    Handles incoming webhook requests from Malwarebytes and posts the event to Slack.
    Example incoming messages can be found at https://api.malwarebytes.com/nebula/v1/docs#section/Events-model

    We want to key in on "threat_events" and "edr_events"

    Returns:
        dict: generic positive response
"""


def subscribe(url=None, vendor="malwarebytes", secret=None):
    """doc"""

    ic(url)
    ic(vendor)
    ic(secret)
    result = Handler(vendor).subscribe(url=url, secret=secret)
    print(result)
    return result


def start(config=None):
    """
    Initialize and configure the Flask app with any configuration variables necessary.

    Args:
        config(dict) - optional flask configuration

    Return:
        Flask app object
    """
    app = create_app(config)
    return app


def lambda_handler(event, context):
    """doc"""
    print("Hello from AWS Lambda using Python" + sys.version + "!")
    return start()


app = start()

if __name__ == "__main__":  # pragma: no cover
    import argparse

    # Setup our CLI to accept an argument to determine what to run.
    parser = argparse.ArgumentParser(description="SMS Pain Survey Sender.")

    parser.add_argument(
        "--subscribe",
        action="store_true",
        dest="subscribe",
        default=False,
        help="Subscribe to a webhook.",
    )

    parser.add_argument(
        "--url",
        action="store",
        dest="url",
        default=None,
        help="The URL of our endpoint.",
    )

    parser.add_argument(
        "--secret",
        action="store",
        dest="secret",
        default=None,
        help="Secret token to validate incoming webhooks for a vendor.",
    )

    parser.add_argument(
        "--vendor",
        action="store",
        dest="vendor",
        default="malwarebytes",
        help="The vendor we're subscribing to.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        dest="DRYRUN",
        default=False,
        help="Do not execute. Display actions only.",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        dest="DEBUG",
        default=False,
        help="Enable debugging.",
    )

    runtime = parser.parse_args()

    if runtime.subscribe:
        subscribe(url=runtime.url, vendor=runtime.vendor, secret=runtime.secret)
    else:
        server_port = os.environ.get("PORT", "8080")
        server_host = os.environ.get("HOST", "127.0.0.1")
        app.run(debug=runtime.DEBUG, port=server_port, host=server_host)
