from controller import create_app


"""
    Handles incoming webhook requests from Malwarebytes and posts the event to Slack.
    Example incoming messages can be found at https://api.malwarebytes.com/nebula/v1/docs#section/Events-model

    We want to key in on "threat_events" and "edr_events"

    Returns:
        dict: generic positive response
"""


def handler():
    app = create_app()
    return app


if __name__ == "__main__":
    app = handler()
    app.run(debug=True)
