from controller import create_app


"""
    Handles incoming webhook requests from Malwarebytes and posts the event to Slack.
    Example incoming messages can be found at https://api.malwarebytes.com/nebula/v1/docs#section/Events-model

    We want to key in on "threat_events" and "edr_events"

    Returns:
        dict: generic positive response
"""


def handler(args=None):
    app = create_app(args)
    return app


if __name__ == "__main__":  # pragma: no cover
    app = handler()
    app.run(debug=True)
