"""
Unit Tests for handlers/handler.py
"""
import os
import requests
import requests_mock
from handlers.handler import Handler


def test_handler_create_random_string():
    rs = Handler.create_random_string()
    assert len(rs) == 40


def test_handler_misconfiguration(flaskapp):
    with flaskapp.test_request_context(
        "/url", method="POST", headers={"X-Adypta": "Nothing"}, json={"coffee": "black"}
    ) as rc:
        response = Handler().misconfiguration()
        assert response.status_code == 500
        assert "Misconfiguration" in str(response.data)


def test_handler_setup_slack_channel(mocker, flaskapp):
    mock_url = "http://localhost.local/"
    mocker.patch.object(Handler, "get_secret", return_value=mock_url)
    os.environ["SLACK_CHANNEL_SECURITY"] = mock_url + "security"
    os.environ["SLACK_CHANNEL_DEVOPS"] = mock_url + "devops"

    url = Handler().setup_slack_channel("security")
    assert url == mock_url + "security"

    url = Handler().setup_slack_channel("junk")
    assert url == mock_url + "devops"

    del os.environ["SLACK_CHANNEL_DEVOPS"]
    mocker.patch.object(Handler, "get_secret", side_effect=Exception)
    url = Handler().setup_slack_channel("junk")
    assert url is None


def test_handler_send_to_slack(mocker, flaskapp):
    mock_json = {"coffee": "black"}
    mock_url = "http://localhost.local/"
    with flaskapp.test_request_context(
        "/", method="POST", headers={"X-Adypta": "Nothing"}, json=mock_json
    ) as rc:
        mocker.patch.object(Handler, "get_secret", side_effect=Exception)
        response = Handler().send_to_slack("junk", {})
        assert response.status_code == 500

        os.environ["SLACK_CHANNEL_DEVOPS"] = mock_url + "devops"
        mocker.patch.object(Handler, "get_secret", return_value=mock_url)
        with requests_mock.Mocker() as m:
            m.post(mock_url + "devops", text="ok", status_code=200)

            response = Handler().send_to_slack("junk", {})
            assert response.status_code == 200

            m.post(mock_url + "devops", exc=requests.exceptions.ConnectTimeout)
            response = Handler().send_to_slack("junk", {})
            assert response.status_code == 500
